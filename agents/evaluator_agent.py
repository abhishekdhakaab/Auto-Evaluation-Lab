from core.scoring import exact_match, score_run
from models.ollama_client import chat

def evaluate(records):
    for r in records:
        r["correct"] = exact_match(r["pred"], r["gold"])
    return score_run(records)



import re
from core.scoring import exact_match, score_run
from models.ollama_client import chat

FINAL_RE = re.compile(r"Final:\s*(Yes|No)\s*$", re.IGNORECASE | re.MULTILINE)

def parse_final_yesno(text: str) -> str | None:
    m = FINAL_RE.search(text)
    return m.group(1).capitalize() if m else None

async def llm_judge_score(judge_model: str, gold_label: str, gold_rationale: str, pred_text: str) -> float:
    """
    Ask a local model to grade the explanation quality on 1..5.
    """
    rubric = (
        "You are a strict evaluator.\n"
        "Score the ASSISTANT'S explanation from 1.0 to 5.0 based on:\n"
        "  (1) Correctness of final Yes/No vs GOLD label\n"
        "  (2) Soundness and clarity of reasoning\n"
        "  (3) Consistency with the gold rationale\n"
        "Output ONLY a number (e.g., 4.0)."
        f"\n\nGOLD LABEL: {gold_label}\nGOLD RATIONALE: {gold_rationale}\n\nASSISTANT:\n{pred_text}\n"
    )
    msgs = [
        {"role": "system", "content": "Return only a numeric score."},
        {"role": "user", "content": rubric},
    ]
    try:
        txt = await chat(judge_model, msgs, temperature=0.0)
        return float(re.findall(r"\d+(?:\.\d+)?", txt)[0])
    except Exception:
        return 3.0  # neutral fallback

async def evaluate_reasoning(records, judge_model: str):
    """
    records: list of dicts with keys {id, prompt, gold, pred_text}
    Returns metrics with both exact label accuracy and avg judge score.
    """
    for r in records:
        label = parse_final_yesno(r["pred_text"]) or ""
        r["pred_label"] = label
        r["correct"] = 1 if label and exact_match(label, r["gold"]) else 0
        r["judge"] = await llm_judge_score(judge_model, r["gold"], r.get("gold_rationale",""), r["pred_text"])
    acc = sum(r["correct"] for r in records) / max(1, len(records))
    judge_avg = sum(r["judge"] for r in records) / max(1, len(records))
    return {"accuracy": acc, "judge_avg": judge_avg, "n": len(records)}

# async def llm_judge_score(model:str, prompt:str, gold:str, pred:str)->float:
#     rubric = (
#         "Score the ASSISTANT answer from 1.0 to 5.0.\n"
#         "Criteria: correctness, clarity, reasoning alignment with GOLD.\n"
#         "Output only the number.\n\n"
#         f"GOLD:\n{gold}\n\nASSISTANT:\n{pred}\n"
#     )
#     msgs=[{"role":"system","content":"You are a strict grader. Output only a number."},
#           {"role":"user","content":rubric}]
#     try:
#         txt = await chat(model, msgs, temperature=0.0)
#         return float(txt.strip())
#     except Exception:
#         return 3.0  # neutral fallback