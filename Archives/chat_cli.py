print("DEBUG: top of chat_cli.py")

import os
import json
import re
from datetime import date, datetime
import mysql.connector
from openai import OpenAI

# --- MySQL config (same as notebooks) ---
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "pantry_user",
    "password": "MyStrongPwd123!",   # <-- your MySQL password
    "database": "smart_pantry",
}

# --- OpenAI config ---
os.environ["OPENAI_API_KEY"] = "REMOVED_KEY"
client = OpenAI()


def get_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)


# --- Tool functions (MySQL-backed, same as Notebook 4) ---

def get_pantry_items() -> list:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT name, category, quantity, unit, expiry_date "
        "FROM pantry ORDER BY expiry_date ASC"
    )
    rows = cur.fetchall()
    conn.close()
    today = date.today()
    items = []
    for name, category, qty, unit, expiry in rows:
        days_left = None
        if expiry:
            days_left = (datetime.strptime(str(expiry), "%Y-%m-%d").date() - today).days
        items.append(
            {
                "name": name,
                "category": category,
                "quantity": qty,
                "unit": unit,
                "expiry_date": str(expiry),
                "days_until_expiry": days_left,
            }
        )
    return items


def get_at_risk_items(threshold_days: int = 3) -> list:
    return [
        {**item, "status": "EXPIRED" if item["days_until_expiry"] < 0 else "AT RISK"}
        for item in get_pantry_items()
        if item["days_until_expiry"] is not None
        and item["days_until_expiry"] <= threshold_days
    ]


def add_pantry_item(name: str, category: str, quantity: float, unit: str, expiry_date: str) -> str:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO pantry (name, category, quantity, unit, expiry_date) "
        "VALUES (%s,%s,%s,%s,%s)",
        (name, category, quantity, unit, expiry_date),
    )
    conn.commit()
    conn.close()
    return f"Added: {quantity} {unit} of '{name}' (expires {expiry_date})."


def remove_pantry_item(name: str) -> str:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM pantry "
        "WHERE LOWER(name) = LOWER(%s) "
        "LIMIT 1",
        (name,),
    )
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return f"Removed '{name}'." if affected > 0 else f"'{name}' not found in pantry."


def update_quantity(name: str, new_quantity: float) -> str:
    if new_quantity <= 0:
        return remove_pantry_item(name)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE pantry SET quantity = %s "
        "WHERE LOWER(name) = LOWER(%s) "
        "LIMIT 1",
        (new_quantity, name),
    )
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return f"Updated '{name}' to {new_quantity}." if affected > 0 else f"'{name}' not found."


# --- Tool schemas and dispatch map ---

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_pantry_items",
            "description": "Retrieve all pantry items with expiry dates. Call before any recipe suggestion.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_at_risk_items",
            "description": "Get items expiring within threshold_days days (default 3). Use for recipe prioritization.",
            "parameters": {
                "type": "object",
                "properties": {
                    "threshold_days": {
                        "type": "integer",
                        "description": "Days threshold. Default 3.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_pantry_item",
            "description": "Add a new ingredient to the pantry.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit": {"type": "string"},
                    "expiry_date": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["name", "category", "quantity", "unit", "expiry_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_pantry_item",
            "description": "Remove an ingredient from the pantry.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_quantity",
            "description": "Update remaining quantity of an item after partial use. Pass 0 to remove.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "new_quantity": {"type": "number"},
                },
                "required": ["name", "new_quantity"],
            },
        },
    },
]

TOOL_MAP = {
    "get_pantry_items":   lambda args: get_pantry_items(),
    "get_at_risk_items":  lambda args: get_at_risk_items(**args),
    "add_pantry_item":    lambda args: add_pantry_item(**args),
    "remove_pantry_item": lambda args: remove_pantry_item(**args),
    "update_quantity":    lambda args: update_quantity(**args),
}

print("Tools loaded:", list(TOOL_MAP.keys()))


SYSTEM_PROMPT = """
You are the Smart Pantry Chef, an AI kitchen assistant specialized in zero-waste cooking.
Your primary goal is to help users reduce household food waste by intelligently using
ingredients before they expire.

Your tools:
- get_pantry_items()  → full inventory with expiry dates and days remaining
- get_at_risk_items() → items expiring within N days (default: 3)
- add_pantry_item()   → add newly purchased ingredients
- remove_pantry_item()→ remove fully used or discarded items
- update_quantity()   → update remaining quantity after partial use

Reasoning rules:
1. NEVER suggest an ingredient not confirmed in the pantry. Always call tools before any recipe suggestion.
2. ALWAYS prioritize at-risk ingredients (expiring within 3 days).
3. Only list pantry-confirmed ingredients. Salt and water may be labeled (assumed).
4. If a recipe requires missing ingredients, say which ones are missing.
5. After every recipe, offer to update the pantry inventory.

Recipe output format:
**Recipe:** [Name]
**Why this recipe?** [At-risk ingredients used, days remaining]
**Ingredients from your pantry:** [list with quantities]
**Assumed staples:** (if any)
**Instructions:** 1–8 concise steps
**Pantry update:** Offer to update quantities.

Tone: Warm, encouraging, and practical. Frame waste reduction as saving money and being resourceful.
"""


def run_agent_turn(messages) -> str:
    """
    Run one complete agent turn using tools when the model emits tool_calls.
    """
    tool_call_count = 0

    while True:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            reply = msg.content
            if tool_call_count > 0:
                print(f"[agent made {tool_call_count} tool call(s) before answering]")
            print("\nChef:\n" + reply + "\n")
            return reply

        messages.append(msg)

        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)
            tool_call_count += 1
            print(f"[tool call {tool_call_count}: {fn_name}({fn_args})]")

            if fn_name in TOOL_MAP:
                result = TOOL_MAP[fn_name](fn_args)
            else:
                result = f"ERROR: unknown tool '{fn_name}'"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, default=str),
                }
            )


def handle_explicit_usage(user_text: str) -> str:
    """
    Simple parser: if the user says 'I used X <name>', update that item directly in MySQL.
    Examples:
    - 'I used 1 egg'
    - 'I used 2 pieces of chicken'
    """
    text = user_text.lower()
    if "i used" not in text:
        return ""

    # Very simple pattern: "I used <number> <name>"
    m = re.search(r"i used\s+(\d+(\.\d+)?)\s+([a-zA-Z ]+)", text)
    if not m:
        return ""

    used_qty = float(m.group(1))
    item_name = m.group(3).strip()

    # Find current quantity of that item
    items = get_pantry_items()
    match = None
    for item in items:
        if item["name"].lower() == item_name:
            match = item
            break

    if not match:
        return f"I could not find '{item_name}' in your pantry table, so I did not update anything."

    current_qty = float(match["quantity"])
    new_qty = current_qty - used_qty
    if new_qty < 0:
        new_qty = 0

    result_msg = update_quantity(match["name"], new_qty)
    return f"{result_msg} (was {current_qty}, used {used_qty}, now {new_qty})."


def chat_loop():
    print("Starting chat loop...")
    print("Type your questions. Type 'exit' to quit.\n")
    conversation = []

    while True:
        user = input("You: ")
        if user.strip().lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        # First, see if this is an explicit "I used X <item>" message
        explicit_update = handle_explicit_usage(user)
        if explicit_update:
            print("\nChef:\n" + explicit_update + "\n")
            conversation.append({"role": "assistant", "content": explicit_update})
            continue

        # Otherwise, let the agent handle it with tools for recipes etc.
        conversation.append({"role": "user", "content": user})
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation
        reply = run_agent_turn(messages)
        conversation.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    print("DEBUG: in __main__ block, calling chat_loop()")
    chat_loop()
