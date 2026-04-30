# 🥬 Smart Pantry Chef

> **The AI agent that looks inside your fridge, spots what's about to expire, and tells you exactly what to cook — before it's too late.**

Smart Pantry Chef is a zero-waste kitchen AI agent powered by GPT-4o mini. It maintains a live inventory of your pantry, identifies ingredients at risk of expiring, suggests grounded recipes using only what you actually have, and updates your inventory after cooking all through a natural language chat interface.


## 🧠 How It Works

Smart Pantry Chef uses the **Tool Use agentic pattern**. Rather than relying on the model's general knowledge (which would hallucinate ingredients), the agent is given structured access to your live MySQL database through five Python tool functions.

```
User Message
     ↓
LLM Decides which tool to call
     ↓
Tool executes against MySQL database
     ↓
LLM receives result and reasons over it
     ↓
Loop repeats until no more tool calls needed
     ↓
Final grounded response delivered
```

The loop is genuinely agentic — the model autonomously decides the sequence of tool calls. A typical recipe suggestion turn involves 2–3 tool calls before the final response is produced.

---

## ✨ Features

- **Zero-hallucination recipes** — every ingredient is verified against the live database before being suggested
- **Expiry-first prioritisation** — the agent always checks what is about to expire before making any recommendation
- **Live pantry dashboard** — scrollable table showing all items with real-time days-remaining status
- **Natural language chat** — ask anything in plain English; the agent handles tool orchestration invisibly
- **Quick-action shortcuts** — one-click buttons for Recipe Ideas, Expiring Soon, Zero-waste Meal, Clear Expired
- **Receipt / label OCR scanning** — photograph a grocery receipt and have all items automatically added to your pantry with estimated expiry dates
- **Inventory management** — add, remove, and update quantities through conversation

---

## 🗂️ Project Structure

```
smart-pantry-chef/
│
├── app.py                        # Flask web application (main entry point)
├── sql_openai_config.py          # Database and API key configuration
│
├── notebooks/
│   ├── 01_database_setup.ipynb   # MySQL schema creation and data seeding
│   ├── 02_tools.ipynb            # Tool functions + OpenAI function schemas
│   ├── 03_prompt_engineering.ipynb # 5-version prompt iteration log (V1→V5)
│   ├── 04_agent_loop.ipynb       # Agentic loop implementation and demo
│   ├── 05_evaluation.ipynb       # LLM-as-judge evaluation across all prompt versions
│   └── 06_interactive_chat.ipynb # Live chat demo in Jupyter
│
└── templates/
    └── index.html                # Chat UI frontend
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| AI Model | GPT-4o mini (OpenAI) |
| Agentic Pattern | Tool Use / Function Calling |
| Backend | Flask (Python) |
| Database | MySQL |
| OCR | EasyOCR |
| Image handling | Pillow (PIL) |
| Frontend | HTML / CSS / JavaScript |

---

## ⚙️ Prerequisites

- Python 3.11+
- MySQL 8.0+
- An OpenAI API key

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/smart-pantry-chef.git
cd smart-pantry-chef
```

### 2. Install Python dependencies

```bash
pip install flask openai mysql-connector-python pillow easyocr pandas matplotlib
```

### 3. Set up the database

Log into MySQL and run the following to create the database and user:

```sql
CREATE DATABASE smart_pantry;
CREATE USER 'pantry_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON smart_pantry.* TO 'pantry_user'@'localhost';
FLUSH PRIVILEGES;
```

Then create the pantry table:

```sql
USE smart_pantry;

CREATE TABLE pantry (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)   NOT NULL,
    category    VARCHAR(50)    NOT NULL,
    quantity    DECIMAL(10,2)  NOT NULL,
    unit        VARCHAR(30)    NOT NULL,
    expiry_date DATE,
    added_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Configure credentials

Open `sql_openai_config.py` and update your credentials:

```python
def get_mysql_config():
    return {
        "host":     "localhost",
        "port":     3306,
        "user":     "pantry_user",
        "password": "your_password",
        "database": "smart_pantry",
    }

def get_openai():
    return "sk-your-openai-api-key"
```

### 5. Start the Flask app

```bash
python app.py
```

Open your browser at `http://localhost:5001`

---

## 🔌 API Endpoints

### `GET /`
Serves the chat UI.

---

### `POST /chat`

Send a natural language message to the Smart Pantry Chef agent.

**Request:**
```json
{ "message": "What should I cook tonight to avoid wasting anything?" }
```

**Response:**
```json
{
  "reply": "**Recipe:** Spinach & Chicken Stir-fry\n**Why this recipe?** Spinach expires in 1 day..."
}
```

---

### `GET /pantry`

Returns the live pantry inventory directly from MySQL — no AI layer involved.

**Response:**
```json
{
  "items": [
    {
      "name": "spinach",
      "category": "vegetable",
      "quantity": 100.0,
      "unit": "grams",
      "expiry_date": "2026-04-28",
      "days_until_expiry": 1
    }
  ]
}
```

---

### `POST /ocr`

Upload an image of a grocery receipt or food label. Items are automatically extracted and added to the pantry.

**Request:** `multipart/form-data` with field `image` (JPEG, PNG, or WEBP)

**Response:**
```json
{
  "ocr_raw": [
    { "text": "Organic Spinach 200g", "confidence": 0.94 }
  ],
  "reply": "✅ Added 2 items:\n• 200 grams of Spinach → Produce · expires 2026-05-02 (estimated)"
}
```

---

## 🤖 The Five Agent Tools

| Tool | Description |
|---|---|
| `get_pantry_items()` | Returns full inventory sorted by expiry date with days-remaining computed |
| `get_at_risk_items(threshold_days)` | Filters to items expiring within N days; flags expired items separately |
| `add_pantry_item(name, category, quantity, unit, expiry_date)` | Inserts a new item with validation |
| `remove_pantry_item(name)` | Deletes by partial name match; handles brand-prefixed names |
| `update_quantity(name, new_quantity)` | Updates remaining quantity; auto-removes if quantity reaches 0 |

---

## 📓 Notebook Guide

Run the notebooks in order for a full walkthrough:

| Notebook | What to do |
|---|---|
| `01_database_setup.ipynb` | Run all cells to create the schema |
| `02_tools.ipynb` | Explore each tool function individually and test database connections |
| `03_prompt_engineering.ipynb` | Read the 5-version prompt iteration log; shows each failure and fix |
| `04_agent_loop.ipynb` | Run the full 4-turn demo conversation to see the agent in action |
| `05_evaluation.ipynb` | Run all cells to execute 15 evaluation turns and generate result charts |
| `06_interactive_chat.ipynb` | Live chat interface — type your own questions directly in Jupyter |

---

## 🔒 Prompt Engineering Summary

The production system prompt was developed across 5 iterations:

| Version | Technique Added | Problem It Solved |
|---|---|---|
| V1 | Nothing | Baseline — hallucinations frequent |
| V2 | Persona assignment | Generic, unfocused responses |
| V3 | Anti-hallucination grounding rule | Model invented ingredients not in pantry |
| V4 | Chain-of-thought (5-step sequence) | Inconsistent expiry prioritisation |
| V5 | Structured output template | Unpredictable response format |

---

## ⚠️ Safety Notes

**Food safety** — The agent does not distinguish between best-before dates (quality guideline) and use-by dates (safety limit). Do not rely on the agent's suggestions for use-by expired items.

**Allergen awareness** — The agent has no knowledge of dietary restrictions or allergies. It will suggest recipes containing any pantry ingredient regardless of personal health requirements.


---

## 🗺️ Future Roadmap

- **Meal planning mode** — plan the week's meals around expiry schedules
- **Multi-agent architecture** — separate Planner, Shopper, and Chef agents
- **Supermarket API integration** — auto-generate shopping lists for pantry gaps

---


﻿# smart_pantry
