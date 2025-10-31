import json, os
from statistics import mean

INDEX_PATH = "experiments/index.json"

def load_index():
    if not os.path.exists(INDEX_PATH):
        return []
    with open(INDEX_PATH) as f:
        return json.load(f)

def save_index(runs):
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, "w") as f:
        json.dump(runs, f, indent=2)

def add_run_entry(run_id:str, model:str, mode:str, acc:float):
    runs = load_index()
    runs.append({"run_id": run_id, "model": model, "mode": mode, "accuracy": acc})
    save_index(runs)
    return runs

def get_trend_summary():
    runs = load_index()
    if not runs:
        return "No prior runs"
    avg_acc = mean([r["accuracy"] for r in runs])
    return f"{len(runs)} total runs, mean accuracy = {avg_acc:.2%}"