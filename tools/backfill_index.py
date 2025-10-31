import json, glob, os
from statistics import mean

INDEX_PATH = "experiments/index.json"

def load(path):
    with open(path) as f:
        return json.load(f)

def main():
    runs = []
    for p in sorted(glob.glob("experiments/*_report.json")):
        try:
            rep = load(p)
            rid = rep.get("run_id") or os.path.basename(p).split("_report.json")[0]
            model = rep.get("model", "unknown")
            domain = rep.get("domain", "math")
            mode = rep.get("mode") if domain == "math" else domain
            acc = rep.get("metrics", {}).get("accuracy", None)
            if acc is None:
                continue
            runs.append({"run_id": rid, "model": model, "mode": mode, "accuracy": acc})
        except Exception as e:
            print(f"[skip] {p}: {e}")

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, "w") as f:
        json.dump(runs, f, indent=2)
    print(f"Wrote {len(runs)} runs to {INDEX_PATH}")

if __name__ == "__main__":
    main()