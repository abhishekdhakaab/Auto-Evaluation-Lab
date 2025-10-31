import re, statistics

def normalize(s:str)->str:
    return re.sub(r"\s+","",s.lower())

def exact_match(pred:str, gold:str)->int:
    return 1 if normalize(pred)==normalize(gold) else 0

def score_run(records):
    # records: [{id, gold, pred, correct(0/1)}]
    acc = sum(r["correct"] for r in records) / max(1,len(records))
    return {"accuracy": acc, "n": len(records)}