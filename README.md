# Smart Pantry Chef — Agentic AI for Zero-Waste Cooking

## Project Overview
An LLM agent that tracks your pantry, reasons about expiration dates,
and suggests recipes that prioritize at-risk ingredients — preventing
food waste through real-time database integration and prompt engineering.

---

## Project Structure

```
smart_pantry/
├── notebooks/
│   ├── 01_database_setup.ipynb      ← Run FIRST: creates DB, loads 50 items
│   ├── 02_tools.ipynb               ← Tool functions + OpenAI tool schemas
│   ├── 03_prompt_engineering.ipynb  ← 5 prompt versions + experiments
│   ├── 04_agent_loop.ipynb          ← Full agentic loop + test turns
│   ├── 05_evaluation.ipynb          ← Metrics + comparison table
│   └── 06_interactive_chat.ipynb    ← Live chat interface (run last)
│   └── sql_openai_config.py         ← Returns the SQL Config and OpenAI API key

├── data/
│   ├── pantry_items.json            ← 50 pantry items (source of truth)
│   ├── pantry.db                    ← SQLite database (auto-created)
│   └── experiment_results.json      ← Saved after running notebook 05
└── requirements.txt
```

---

## Setup Instructions (VS Code)

### Step 1: Install Python dependencies
Open a terminal in VS Code (Ctrl+`) and run:
```bash
pip install -r requirements.txt
```

### Step 2: Set your OpenAI API key
**Option A — Environment variable (recommended):**
```bash
# Mac/Linux
export OPENAI_API_KEY=sk-your-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY = "sk-your-key-here"
```

**Option B — Inline in any notebook:**
Uncomment and edit this line at the top of any notebook:
```python
os.environ['OPENAI_API_KEY'] = 'sk-your-key-here'
```

### Step 3: Select Python kernel in VS Code
- Open any `.ipynb` file
- Click "Select Kernel" (top right) → choose your Python environment

### Step 4: Run notebooks in order
```
01 → 02 → 03 → 04 → 05 → 06
```
Notebooks 02–06 are self-contained but the database must exist first (notebook 01).

---

## Notebook Guide

| Notebook | Purpose | Key concepts |
|---|---|---|
| 01 | Database setup | SQLite, JSON loading, schema design |
| 02 | Tool functions | Function calling, tool schemas, dispatcher |
| 03 | Prompt engineering | 5 prompt iterations, A/B comparison |
| 04 | Agent loop | Think → call tool → observe → think loop |
| 05 | Evaluation | Metrics: hallucination, grounding, structure |
| 06 | Interactive chat | Live conversation with full tool transparency |

---

## Sample Conversations to Try (Notebook 06)

```
"What should I cook tonight to avoid wasting anything?"
"Suggest a breakfast using items expiring soon."
"I just bought 300g of ground turkey expiring 2025-03-28. Add it."
"What's in my pantry right now?"
"I made the recipe — I used all the spinach and 1 piece of chicken."
"Can you suggest an Asian-inspired dish with what's about to expire?"
"Remove the bread — it went moldy."
```

---

## Why This Project Needs Prompt Engineering + Function Calling

A standalone LLM cannot do this task because:
1. **No real-time inventory** — it hallucinates ingredients
2. **No expiry awareness** — it cannot reason about today's date vs. expiration
3. **No state updates** — it cannot modify the pantry after cooking

Prompt engineering is needed because:
1. RAG grounds the data but unfocused prompts still produce vague output
2. Chain-of-thought forces step-by-step expiry reasoning
3. Structured output format makes responses consistent and auditable
4. Persona + tone guides the model toward practical, encouraging responses

---

## Resetting the Pantry

To reload all 50 original items and start fresh, run this in any notebook:
```python
conn = get_connection()
conn.execute('DELETE FROM pantry')
conn.commit()
conn.close()
load_from_json(JSON_PATH)
```
Or use the `reset_and_reload()` function in notebook 01.
# smart_pantry
# smart_pantry
# smart_pantry
