from dataclasses import dataclass
import json, random

@dataclass
class Item:
    id: str
    prompt: str
    answer: str
    domain: str
    meta: dict | None = None

def make_simple_math(n:int=10, seed:int=0, mode:str="single"):
    """
    mode = "single" (a±b), "multi" (2-step), "negatives" (includes negatives), "carry" (bigger numbers)
    """
    random.seed(seed)
    items=[]
    for i in range(n):
        if mode == "single":
            a,b = random.randint(1,20), random.randint(1,20)
            op = random.choice(["+","-"])
            ans = a+b if op=="+" else a-b
            prompt = f"{a} {op} {b} = ?"
        elif mode == "multi":
            # two-step arithmetic (a±b±c)
            a,b,c = random.randint(1,30), random.randint(1,30), random.randint(1,30)
            op1, op2 = random.choice(["+","-"]), random.choice(["+","-"])
            ans = (a+b if op1=="+" else a-b)
            ans = ans + c if op2=="+" else ans - c
            prompt = f"{a} {op1} {b} {op2} {c} = ?"
        elif mode == "negatives":
            a,b = random.randint(-20,20), random.randint(-20,20)
            op = random.choice(["+","-"])
            ans = a+b if op=="+" else a-b
            prompt = f"{a} {op} {b} = ?"
        elif mode == "carry":
            a,b = random.randint(50,999), random.randint(50,999)
            op = random.choice(["+","-"])
            ans = a+b if op=="+" else a-b
            prompt = f"{a} {op} {b} = ?"
        else:
            raise ValueError(f"unknown mode: {mode}")

        items.append(Item(
            id=f"math-{mode}-{i}",
            prompt=prompt,
            answer=str(ans),
            domain="math",
            meta={"mode": mode}
        ))
    return items

def save_benchmark(items, path:str):
    with open(path, "w") as f:
        json.dump([item.__dict__ for item in items], f, indent=2)

        # --- Reasoning dataset (binary "Yes/No" with explanation) ---

def make_reasoning(n: int = 10, seed: int = 0):
    """
    Generate simple logic/entailment tasks that require an explanation.
    Gold is 'Yes' or 'No' + a reference rationale string.
    """
    import random
    random.seed(seed)
    items = []

    # A few templates
    templates = [
        # syllogism
        ("All {A} are {B}. {X} is a {A}. Is {X} a {B}?",
         lambda A,B,X: ("Yes", f"By universal rule 'All {A} are {B}', and {X} is {A}, so {X} is {B}.")),
        # denial of the antecedent
        ("If {A} then {B}. Not {A}. Is {B} true?",
         lambda A,B,_: ("No", f"Denying antecedent is invalid; from not {A} we cannot infer {B}.")),
        # modus ponens
        ("If {A} then {B}. {A}. Is {B} true?",
         lambda A,B,_: ("Yes", f"Modus ponens: {A} ⇒ {B}; given {A}, therefore {B}.")),
        # subset/entailment
        ("Every {A} likes {B}. {X} is a {A}. Does {X} like {B}?",
         lambda A,B,X: ("Yes", f"Universal statement applies to all {A}; {X} is {A}, so yes.")),
        # contrapositive intuition
        ("If {A} then {B}. {B} is false. Is {A} false?",
         lambda A,B,_: ("Yes", f"Contrapositive: If A→B then ¬B→¬A; since ¬{B}, ¬{A}."))
    ]
    nouns = ["cats", "teachers", "robots", "scientists", "painters", "drivers"]
    props = ["mammals", "smart", "licensed", "tired", "happy", "kind"]
    names = ["Alex", "Sam", "Riley", "Jordan", "Casey", "Taylor"]

    for i in range(n):
        t, gold_fn = random.choice(templates)
        A = random.choice(nouns); B = random.choice(props); X = random.choice(names)
        prompt = t.format(A=A, B=B, X=X)
        yesno, rationale = gold_fn(A,B,X)
        # ask model to answer + explain + put final label
        user = (
            prompt + "\n\n"
            "Answer Yes or No and explain in 2–3 sentences.\n"
            "Put your final decision on a new last line exactly as: Final: Yes   or   Final: No"
        )
        items.append(Item(
            id=f"reason-{i}",
            prompt=user,
            answer=yesno,     # gold label only; rationale is free-form
            domain="reason",
            meta={"rationale": rationale}
        ))
    return items