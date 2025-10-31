import yaml, os

CONFIG_PATH = "config/governance.yaml"

def load_rules():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def enforce_rate_limit(n_items:int, rules:dict):
    limit = rules.get("max_items_per_round", 20)
    if n_items > limit:
        raise ValueError(f"Too many items! max allowed is {limit}")