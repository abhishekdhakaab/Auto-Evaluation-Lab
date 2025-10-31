import json, os, time

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f: json.dump(obj, f, indent=2)

def timestamp():
    return time.strftime("%Y%m%d-%H%M%S")