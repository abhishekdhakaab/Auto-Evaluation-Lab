# orchestrator.py
from __future__ import annotations

import os
from typing import Optional, Dict, Any, List

from core.io import write_json, timestamp
from core.governance import load_rules, enforce_rate_limit
from core.memory import add_run_entry, get_trend_summary

from agents.dataset_agent import (
    make_simple_math,
    make_reasoning,
    save_benchmark,
)
from agents.analyst_agent import summarize_metrics
from agents.evaluator_agent import evaluate as eval_math
from agents.evaluator_agent import evaluate_reasoning
from models.ollama_client import chat


# --------- Global config ---------
CANDIDATE = os.environ.get("CANDIDATE_MODEL", "qwen2.5:0.5b-instruct")
MODES_ORDER = ["single", "multi", "carry"]  # for math only


def _suggest_next_mode(current: str, acc: float) -> str:
    """Simple scheduler for math difficulty."""
    if current not in MODES_ORDER:
        return "single"
    i = MODES_ORDER.index(current)
    if acc >= 0.90 and i < len(MODES_ORDER) - 1:
        return MODES_ORDER[i + 1]
    if acc < 0.60 and i > 0:
        return MODES_ORDER[i - 1]
    return current


async def run_round(
    n_items: int = 10,
    outdir: str = "experiments",
    *,
    domain: str = "math",          # "math" | "reason"
    mode: str = "single",          # only used for domain="math"
    judge_model: Optional[str] = None,
    seed: int = 0,
) -> Dict[str, Any]:
    """
    One evaluation round:
      - builds a dataset
      - queries local model via Ollama
      - scores (exact-match for math, LLM-as-judge for reasoning)
      - writes JSON/MD artifacts
      - appends to experiments/index.json
    """

    os.makedirs(outdir, exist_ok=True)

    # ---- Governance checks
    rules = load_rules()
    enforce_rate_limit(n_items, rules)

    run_id = timestamp()
    bench_path = f"{outdir}/{run_id}_benchmark.json"

    # ---- Build dataset
    if domain == "math":
        items = make_simple_math(n_items, seed=seed, mode=mode)
    elif domain == "reason":
        items = make_reasoning(n_items, seed=seed)
    else:
        raise ValueError(f"Unknown domain: {domain}")
    save_benchmark(items, bench_path)

    # ---- Generate predictions
    records: List[Dict[str, Any]] = []
    if domain == "math":
        for it in items:
            msgs = [
                {"role": "system", "content": "Answer with only the final number."},
                {"role": "user", "content": it.prompt},
            ]
            pred = await chat(CANDIDATE, msgs)
            records.append(
                {
                    "id": it.id,
                    "prompt": it.prompt,
                    "gold": it.answer,
                    "pred": pred,
                    "mode": getattr(it, "meta", {}).get("mode", mode),
                }
            )
        metrics = eval_math(records)
        suggested = _suggest_next_mode(mode, metrics["accuracy"])
    else:  # reasoning
        for it in items:
            msgs = [
                {
                    "role": "system",
                    "content": (
                        "Provide brief reasoning and end with a final decision line "
                        "exactly as: 'Final: Yes' or 'Final: No'."
                    ),
                },
                {"role": "user", "content": it.prompt},
            ]
            pred_text = await chat(CANDIDATE, msgs, temperature=0.2)
            records.append(
                {
                    "id": it.id,
                    "prompt": it.prompt,
                    "gold": it.answer,  # Yes/No
                    "gold_rationale": getattr(it, "meta", {}).get("rationale", ""),
                    "pred_text": pred_text,
                }
            )
        if not judge_model:
            judge_model = CANDIDATE  # default to candidate model as judge
        metrics = await evaluate_reasoning(records, judge_model)
        suggested = None  # not applicable for reasoning

    # ---- Persist artifacts
    records_path = f"{outdir}/{run_id}_records.json"
    report_path = f"{outdir}/{run_id}_report.json"
    md_path = f"{outdir}/{run_id}_report.md"

    report: Dict[str, Any] = {
        "run_id": run_id,
        "model": CANDIDATE,
        "domain": domain,
        "mode": (mode if domain == "math" else None),
        "metrics": metrics,
        "sample": records[:3],
        "params": {
            "n_items": n_items,
            "seed": seed,
            "judge_model": judge_model if domain == "reason" else None,
        },
    }

    write_json(records_path, records)
    write_json(report_path, report)

    md = (
        f"# AutoEval Lab Report ({run_id})\n\n"
        f"**Model:** {CANDIDATE}\n\n"
        f"**Domain:** {domain}\n"
        f"{f'**Mode:** {mode}\\n' if domain == 'math' else ''}"
        f"**Metrics:** {metrics}\n\n"
        f"{summarize_metrics(metrics)}\n"
    )
    if suggested:
        md += f"**Next suggested mode:** {suggested}\n"
    with open(md_path, "w") as f:
        f.write(md)

    # ---- Update experiment memory (for plots)
    try:
        add_run_entry(run_id, CANDIDATE, (mode if domain == "math" else domain), metrics["accuracy"])
        print("Trend:", get_trend_summary())
    except Exception as e:
        print(f"[warn] failed to update experiments/index.json: {e}")

    # Attach convenience fields to return value
    report["suggested_next_mode"] = suggested
    return report


async def run_experiment(
    rounds: int = 5,
    *,
    start_mode: str = "single",    # used when domain="math"
    n_items: int = 12,
    outdir: str = "experiments",
    plateau_delta: float = 0.01,   # minimum accuracy improvement to continue
    domain: str = "math",          # "math" | "reason"
    judge_model: Optional[str] = None,
    seed: int = 0,
) -> Dict[str, Any]:
    """
    Multi-round autonomous loop with early stopping if accuracy gains plateau.
    """
    mode = start_mode
    best_acc = -1.0
    history: List[Dict[str, Any]] = []

    for r in range(1, rounds + 1):
        print(f"\n=== ROUND {r}/{rounds} | domain={domain} | mode={mode if domain=='math' else '-'} ===")
        rep = await run_round(
            n_items=n_items,
            outdir=outdir,
            domain=domain,
            mode=mode,
            judge_model=judge_model,
            seed=seed + r,  # vary the dataset slightly per round
        )

        acc = rep["metrics"]["accuracy"]
        history.append(
            {
                "round": r,
                "run_id": rep.get("run_id", ""),
                "domain": domain,
                "mode": (mode if domain == "math" else None),
                "accuracy": acc,
            }
        )

        # Decide next difficulty (math only)
        if domain == "math":
            mode = rep.get("suggested_next_mode", mode)

        # Early stopping on plateau
        improvement = max(0.0, acc - (best_acc if best_acc >= 0 else 0.0))
        if acc > best_acc:
            best_acc = acc

        print(f"Round {r} accuracy: {acc:.2%} | best: {best_acc:.2%} | improvement: {improvement:.2%}")
        if r > 1 and improvement < plateau_delta:
            print(f"Early stop: improvement < {plateau_delta:.2%}")
            break

    # Write experiment summary
    summary = {
        "rounds_requested": rounds,
        "rounds_run": len(history),
        "domain": domain,
        "start_mode": (start_mode if domain == "math" else None),
        "final_mode": (history[-1]["mode"] if domain == "math" else None),
        "best_accuracy": best_acc,
        "history": history,
    }
    exp_id = timestamp()
    write_json(f"{outdir}/{exp_id}_experiment_summary.json", summary)
    print("\n=== EXPERIMENT SUMMARY ===")
    print(summary)
    return summary