def summarize_metrics(metrics:dict)->str:
    acc = metrics["accuracy"]
    n = metrics["n"]
    verdict = "strong" if acc>=0.9 else ("decent" if acc>=0.6 else "weak")
    return (
        f"Items: {n}\n"
        f"Accuracy: {acc:.2%}\n"
        f"Assessment: {verdict}\n"
        f"Next: increase difficulty if >=0.9; else keep; if <0.6, simplify.\n"
    )

def next_mode_suggestion(current_mode:str, acc:float) -> str:
    order = ["single", "multi", "carry"]
    if current_mode not in order:
        return "single"
    idx = order.index(current_mode)
    if acc >= 0.90 and idx < len(order)-1:
        return order[idx+1]
    if acc < 0.60 and idx > 0:
        return order[idx-1]
    return current_mode