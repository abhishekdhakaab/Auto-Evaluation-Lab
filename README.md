# 🧠 AutoEval Lab  
### An Agentic AI Evaluation Framework (Local & Free)

AutoEval Lab is an **autonomous evaluation framework** for local LLMs (e.g., Ollama models like Gemma or Qwen).  
It automatically generates test problems, evaluates model responses, and tracks performance trends —  
mimicking how “agentic” AI systems **reflect, assess, and improve** themselves over time.

---

## 🚀 Features

✅ **Fully local** — works with Ollama (no paid APIs needed)  
✅ **Agentic architecture** — multiple agents (Dataset, Evaluator, Judge, Memory) coordinate to evaluate models  
✅ **Supports multiple domains** — Math & Reasoning  
✅ **Dynamic difficulty** — test adapts based on model accuracy  
✅ **Evaluation memory** — tracks all runs with long-term statistics  
✅ **Dashboard & charts** — visualize model improvement trends  

---

## 🧩 Architecture Overview

The system is composed of autonomous components:

| Component | Role |
|------------|------|
| `dataset_agent` | Generates math or reasoning test problems |
| `ollama_client` | Sends prompts to a local model (Gemma, Qwen, etc.) |
| `evaluator_agent` | Grades answers automatically or with LLM-as-judge |
| `memory` | Logs accuracy trends across runs |
| `governance` | Enforces run limits & safety rules |
| `plots` / `dashboard` | Visualizes accuracy trends and past experiments |

Data flow:

```
Dataset Agent → Model (Ollama) → Evaluator → Report → Memory → Dashboard
```

---

## 🧪 Usage

### 1️⃣ Run a quick evaluation
```bash
python app.py --n 12 --model qwen2.5:0.5b-instruct
```
Example output:
```
=== REPORT ===
{'accuracy': 0.91, 'n': 12}
```

### 2️⃣ Run a multi-round experiment
Automatically adjusts difficulty and tracks progress.
```bash
python app.py --rounds 5 --domain math
```

### 3️⃣ Generate trend plots
```bash
python -m plots.plot_trend
```
Outputs: `experiments/accuracy_trend.png`

### 4️⃣ Launch the dashboard
```bash
streamlit run dashboard/app.py
```

Explore:
- Accuracy over time
- Run-level reports
- Detailed answers per question

---

## 📊 Example Output Files

All experiments are saved under `/experiments/`:

| File | Description |
|------|--------------|
| `*_benchmark.json` | Generated test set |
| `*_records.json` | Model answers |
| `*_report.json` | Summary metrics |
| `*_report.md` | Human-readable report |
| `index.json` | Cumulative history for trend analysis |

---

## 🧠 How It Works

1. **Task Generation:** Creates math or logic problems.  
2. **Model Evaluation:** Sends tasks to local LLMs via Ollama.  
3. **Auto-Grading:** Scores answers automatically (math) or with judge model (reasoning).  
4. **Memory Logging:** Saves results to `experiments/index.json`.  
5. **Self-Reflection (Next Step):** Plans harder/easier tests for next rounds.  

---

## 🧩 Example Extensions

Future ideas (for advanced users):
- Self-correction loops (model reflects on its wrong answers)
- Prompt refinement agents
- Bias & robustness testing
- Fine-tuning using LoRA adapters
- Multi-model comparison tournaments

---

## 🧰 Requirements

- **Python ≥ 3.9**
- **Ollama** (running locally)
- Dependencies:
  ```bash
  pip install typer aiohttp streamlit matplotlib pandas
  ```

---

## 📄 Folder Structure

```
auto-eval-lab/
│
├── app.py                # CLI entrypoint
├── orchestrator.py       # Controls evaluation rounds
├── agents/
│   ├── dataset_agent.py
│   ├── evaluator_agent.py
│   └── analyst_agent.py
├── core/
│   ├── governance.py
│   ├── memory.py
│   ├── io.py
│   └── scoring.py
├── models/
│   └── ollama_client.py
├── plots/
│   └── plot_trend.py
├── dashboard/
│   └── app.py
└── experiments/          # Output folder (auto-created)
```

---

## 💡 Project Pitch (for README/Resume)

> “Built an autonomous local AI evaluation framework that benchmarks LLM reasoning and math capabilities using a multi-agent architecture. Includes dataset generation, automatic grading, trend tracking, and visualization — fully local (Ollama-based) and self-improving through adaptive feedback loops.”

---

## 🧾 License
MIT License © 2025 Abhishek Dhaka

---
