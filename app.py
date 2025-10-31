# app.py
import os
import asyncio
import typer

from orchestrator import run_round, run_experiment

app = typer.Typer(add_completion=False)

# ---------- helpers ----------
def _run_eval(n: int, model: str, mode: str, domain: str, judge_model: str | None):
    os.environ["CANDIDATE_MODEL"] = model
    report = asyncio.run(
        run_round(
            n_items=n,
            mode=mode,
            domain=domain,
            judge_model=judge_model,
        )
    )
    print("\n=== REPORT ===")
    print(report["metrics"])
    if domain == "math":
        print("Suggested next mode:", report.get("suggested_next_mode"))

def _run_experiment(
    rounds: int,
    start_mode: str,
    n: int,
    model: str,
    plateau_delta: float,
    domain: str,
    judge_model: str | None,
):
    os.environ["CANDIDATE_MODEL"] = model
    asyncio.run(
        run_experiment(
            rounds=rounds,
            start_mode=start_mode,
            n_items=n,
            plateau_delta=plateau_delta,
            domain=domain,
            judge_model=judge_model,
        )
    )

# ---------- typer commands ----------
@app.command("eval")
def eval_cmd(
    n: int = 10,
    model: str = "qwen2.5:0.5b-instruct",
    mode: str = "single",                # used for math only
    domain: str = "math",                # "math" | "reason"
    judge_model: str = "",               # optional, for domain="reason"
):
    jm = judge_model or None
    _run_eval(n=n, model=model, mode=mode, domain=domain, judge_model=jm)

@app.command("experiment")
def experiment_cmd(
    rounds: int = 5,
    start_mode: str = "single",          # math only
    n: int = 12,
    model: str = "qwen2.5:0.5b-instruct",
    plateau_delta: float = 0.01,
    domain: str = "math",                # "math" | "reason"
    judge_model: str = "",               # optional, for domain="reason"
):
    jm = judge_model or None
    _run_experiment(
        rounds=rounds,
        start_mode=start_mode,
        n=n,
        model=model,
        plateau_delta=plateau_delta,
        domain=domain,
        judge_model=jm,
    )

# ---------- argparse fallback ----------
if __name__ == "__main__":
    import sys
    import argparse

    # If user explicitly calls a Typer subcommand, delegate to Typer.
    if len(sys.argv) > 1 and sys.argv[1] in {"eval", "experiment"}:
        app()
    else:
        parser = argparse.ArgumentParser(description="AutoEval Lab CLI (fallback)")
        parser.add_argument("--n", type=int, default=10, help="Number of items per round")
        parser.add_argument("--model", type=str, default="qwen2.5:0.5b-instruct", help="Candidate model (Ollama)")
        parser.add_argument("--mode", type=str, default="single", help="Difficulty mode (math only)")
        parser.add_argument("--domain", type=str, default="math", choices=["math", "reason"], help="Evaluation domain")
        parser.add_argument("--judge-model", type=str, default="", help="Judge model for reasoning domain (optional)")

        # experiment options (set --rounds>0 to run multi-round experiment)
        parser.add_argument("--rounds", type=int, default=0, help="If >0, run a self-improving experiment for N rounds")
        parser.add_argument("--start-mode", type=str, default="single", help="Starting difficulty (math only)")
        parser.add_argument("--plateau-delta", type=float, default=0.01, help="Early-stop threshold on accuracy gains")

        args = parser.parse_args()
        jm = args.judge_model or None

        if args.rounds and args.rounds > 0:
            _run_experiment(
                rounds=args.rounds,
                start_mode=args.start_mode,
                n=args.n,
                model=args.model,
                plateau_delta=args.plateau_delta,
                domain=args.domain,
                judge_model=jm,
            )
        else:
            _run_eval(
                n=args.n,
                model=args.model,
                mode=args.mode,
                domain=args.domain,
                judge_model=jm,
            )