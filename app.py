print("DEBUG: starting Smart Pantry Chef (Flask)")

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'notebooks'))
import json
import io
import sql_openai_config
from datetime import date, datetime

import mysql.connector
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from PIL import Image

_ocr_reader = None
def get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        import easyocr
        print("Loading EasyOCR model (first use)…")
        _ocr_reader = easyocr.Reader(['en'], gpu=False)
        print("EasyOCR ready.")
    return _ocr_reader

MYSQL_CONFIG = sql_openai_config.get_mysql_config()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    OPENAI_KEY = sql_openai_config.get_openai()

os.environ["OPENAI_API_KEY"] = OPENAI_KEY
client = OpenAI()

app = Flask(__name__)


def get_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)


def get_pantry_items() -> list:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "SELECT name, category, quantity, unit, expiry_date "
        "FROM pantry ORDER BY id DESC"
    )
    rows = cur.fetchall()
    conn.close()

    today = date.today()
    items = []
    for name, category, qty, unit, expiry in rows:
        days_left = None
        if expiry:
            days_left = (
                datetime.strptime(str(expiry), "%Y-%m-%d").date() - today
            ).days
        items.append({
            "name": name,
            "category": category,
            "quantity": float(qty),
            "unit": unit,
            "expiry_date": str(expiry) if expiry else None,
            "days_until_expiry": days_left,
        })
    return items


def get_at_risk_items(threshold_days: int = 3) -> list:
    return [
        {**item, "status": "EXPIRED" if item["days_until_expiry"] < 0 else "AT RISK"}
        for item in get_pantry_items()
        if item["days_until_expiry"] is not None
        and item["days_until_expiry"] <= threshold_days
    ]


def _validate_and_normalize_expiry(expiry_date):
    if not expiry_date or str(expiry_date).strip() == "":
        return None
    expiry_date = str(expiry_date).strip()
    try:
        datetime.strptime(expiry_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"expiry_date '{expiry_date}' is not a valid YYYY-MM-DD date")
    return expiry_date


def add_pantry_item(name, category, quantity, unit, expiry_date):
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        return f"Refused to add '{name}' because quantity='{quantity}' is invalid."
    if quantity <= 0:
        return f"Refused to add '{name}' with non-positive quantity ({quantity})."
    try:
        expiry = _validate_and_normalize_expiry(expiry_date)
    except ValueError as e:
        return f"Refused to add '{name}': {e}."
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO pantry (name, category, quantity, unit, expiry_date) "
        "VALUES (%s,%s,%s,%s,%s)",
        (name, category, quantity, unit, expiry),
    )
    conn.commit()
    conn.close()
    return f"Added: {quantity} {unit} of '{name}' (expires {expiry or 'unknown'})."


def remove_pantry_item(name):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "DELETE FROM pantry WHERE LOWER(name) LIKE %s",
        (f"%{name.lower()}%",)
    )
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return (
        f"Removed {affected} row(s) matching '{name}'."
        if affected > 0
        else f"'{name}' not found in pantry."
    )


def update_quantity(name, new_quantity):
    try:
        new_quantity = float(new_quantity)
    except (TypeError, ValueError):
        return f"Could not update '{name}' because new_quantity='{new_quantity}' is invalid."
    if new_quantity <= 0:
        return remove_pantry_item(name)
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE pantry SET quantity = %s WHERE LOWER(name) LIKE %s LIMIT 1",
        (new_quantity, f"%{name.lower()}%")
    )
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return f"Updated '{name}' to {new_quantity}." if affected > 0 else f"'{name}' not found."


def purge_expired_items(include_no_expiry: bool = False) -> dict:
    today_str = date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    cur  = conn.cursor()

    if include_no_expiry:
        # Two separate queries UNIONed — avoids param count mismatch with OR + IS NULL
        cur.execute(
            "SELECT name, expiry_date FROM pantry "
            "WHERE expiry_date <= %s OR expiry_date IS NULL",
            (today_str,)
        )
    else:
        cur.execute(
            "SELECT name, expiry_date FROM pantry WHERE expiry_date <= %s",
            (today_str,)
        )

    rows = cur.fetchall()

    if not rows:
        conn.close()
        return {"deleted_count": 0, "deleted_items": [], "message": "No expired items found."}

    # Collect the exact IDs to delete so nothing is missed
    deleted_names = [r[0] for r in rows]
    placeholders  = ",".join(["%s"] * len(deleted_names))
    cur.execute(
        f"DELETE FROM pantry WHERE name IN ({placeholders})",
        tuple(deleted_names)
    )
    affected = cur.rowcount
    conn.commit()
    conn.close()

    deleted = [
        {"name": r[0], "expiry_date": str(r[1]) if r[1] else "no date"}
        for r in rows
    ]
    return {
        "deleted_count": affected,
        "deleted_items": deleted,
        "message": f"Purged {affected} expired item(s).",
    }


SYSTEM_PROMPT_TEMPLATE = """
Today's date is {today}.
You are the Smart Pantry Chef, an AI kitchen assistant focused on zero-waste cooking.
Rules:
1)  Always call pantry tools before suggesting recipes.
2)  Prioritize items expiring within 3 days.
3)  Never invent ingredients not in the pantry (salt and water are assumed staples).
4)  Clearly list missing ingredients when a recipe needs them.
5)  Never insert items with negative quantities or invalid dates.
6)  Keep responses concise and structured.
7)  When adding items, always assign the most appropriate category from this list:
    Produce, Dairy, Meat & Seafood, Bakery, Frozen, Beverages,
    Canned & Jarred, Dry Goods & Pasta, Snacks, Condiments & Sauces,
    Spices & Seasonings, Oils & Vinegars, Baking, Breakfast, Personal Care, Other.
8)  If no expiry date is visible, estimate one based on the product type using these
    shelf-life guidelines (from today's date {today}):
      - Fresh produce (leafy greens, berries)    → +5 days
      - Fresh produce (root veg, citrus, apples) → +14 days
      - Fresh meat & poultry                     → +3 days
      - Fresh seafood                            → +2 days
      - Deli / cooked meats                      → +5 days
      - Dairy (milk, cream, yogurt)              → +7 days
      - Dairy (hard cheese)                      → +30 days
      - Eggs                                     → +21 days
      - Bread / bakery                           → +7 days
      - Frozen items                             → +180 days
      - Canned / jarred goods                    → +365 days
      - Dry goods (pasta, rice, flour, oats)     → +365 days
      - Snacks (chips, crackers, nuts)           → +90 days
      - Condiments (opened)                      → +90 days
      - Spices & seasonings                      → +365 days
      - Oils                                     → +180 days
      - Beverages (juice, milk-based)            → +7 days
      - Beverages (soda, water, shelf-stable)    → +180 days
      - Breakfast cereals                        → +180 days
    Always store the estimated date as YYYY-MM-DD format.
9)  If remove_pantry_item returns 'not found', call get_pantry_items first to find
    the exact name in the database, then retry removal using that exact name.
10) NEVER add non-food or non-beverage items to the pantry. Skip items such as:
    parchment paper, aluminum foil, plastic wrap, zip-lock bags, paper towels,
    cleaning supplies, soap, detergent, or any household item that is not eaten
    or drunk. Silently ignore these — do not call add_pantry_item for them.
11) When the user asks to delete, remove, clear, or purge ALL expired items,
    ALWAYS call purge_expired_items() in a single tool call. Never loop through
    items one by one with remove_pantry_item for bulk expiry cleanup.
"""

OCR_PARSE_PROMPT_TEMPLATE = """
Today's date is {today}.
You are a pantry data extraction assistant.

The user uploaded an image of a grocery receipt, food label, or ingredient list.
Raw OCR text extracted from that image:

{ocr_text}

Tasks:
1.  Parse this text and identify food/grocery items with their quantities and units.
1b. SKIP non-food items entirely — do not add parchment paper, aluminum foil, plastic
    wrap, zip-lock bags, paper towels, cleaning supplies, soap, or any item that is not
    eaten or drunk. Do not call add_pantry_item for these. Omit them from the summary.
2.  For each valid food item, call add_pantry_item to add it to the pantry.
3.  Automatically assign the most appropriate category from this list:
      - Produce             → fresh fruits, vegetables, herbs
      - Dairy               → milk, cheese, yogurt, butter, eggs
      - Meat & Seafood      → chicken, beef, fish, shrimp, deli meats
      - Bakery              → bread, rolls, cakes, pastries
      - Frozen              → frozen meals, ice cream, frozen vegetables
      - Beverages           → juice, soda, water, coffee, tea
      - Canned & Jarred     → canned beans, soups, tomato sauce, pickles
      - Dry Goods & Pasta   → rice, pasta, flour, oats, lentils
      - Snacks              → chips, crackers, nuts, granola bars
      - Condiments & Sauces → ketchup, mayo, hot sauce, dressings
      - Spices & Seasonings → salt, pepper, cumin, paprika
      - Oils & Vinegars     → olive oil, vegetable oil, vinegar
      - Baking              → baking soda, baking powder, sugar, yeast
      - Breakfast           → cereal, pancake mix, syrup
      - Other               → anything that doesn't fit above
4.  For expiry dates:
    - If a clear expiry/best-by date is visible in the OCR text, use that as YYYY-MM-DD.
    - If NO expiry date is visible, estimate from today ({today}) using the shelf-life
      guidelines below.
4b. DATE SANITY CHECK — after determining any date (from label OR estimated), check if
    it is earlier than or equal to today ({today}). If the date is in the past or is
    today, discard it and re-estimate from today ({today}) using the shelf-life
    guidelines below. Mark these "(re-estimated — label date was expired)" in the summary.
    Shelf-life guidelines (add to today {today}):
      Fresh produce (leafy greens, berries)    → +5 days
      Fresh produce (root veg, citrus, apples) → +14 days
      Fresh meat & poultry                     → +3 days
      Fresh seafood                            → +2 days
      Deli / cooked meats                      → +5 days
      Dairy (milk, cream, yogurt)              → +7 days
      Dairy (hard cheese)                      → +30 days
      Eggs                                     → +21 days
      Bread / bakery                           → +7 days
      Frozen items                             → +180 days
      Canned / jarred goods                    → +365 days
      Dry goods (pasta, rice, flour, oats)     → +365 days
      Snacks (chips, crackers, nuts)           → +90 days
      Condiments (opened)                      → +90 days
      Spices & seasonings                      → +365 days
      Oils                                     → +180 days
      Beverages (juice, milk-based)            → +7 days
      Beverages (soda, water, shelf-stable)    → +180 days
      Breakfast cereals                        → +180 days
5.  If quantity is not specified, assume 1 unit.
6.  After adding all items, reply with a summary like:
    ✅ Added X items:
    • [qty] [unit] of [name] → [Category] · expires [YYYY-MM-DD] (estimated)
    • [qty] [unit] of [name] → [Category] · expires [YYYY-MM-DD] (from label)
    • [qty] [unit] of [name] → [Category] · expires [YYYY-MM-DD] (re-estimated — label date was expired)
    ⛔ Skipped (non-food): [name], [name]
    Always include the skipped section if any non-food items were found.
7.  If no food items are found at all, say so clearly.
"""

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_pantry_items",
            "description": "Retrieve all pantry items with expiry dates and days remaining.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_at_risk_items",
            "description": "Get items expiring within threshold_days days (default 3).",
            "parameters": {
                "type": "object",
                "properties": {
                    "threshold_days": {
                        "type": "integer",
                        "description": "Days threshold. Default 3.",
                        "minimum": 1,
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
                    "name":        {"type": "string"},
                    "category":    {"type": "string"},
                    "quantity":    {"type": "number", "minimum": 0.01},
                    "unit":        {"type": "string"},
                    "expiry_date": {"type": "string", "description": "YYYY-MM-DD or empty string."},
                },
                "required": ["name", "category", "quantity", "unit", "expiry_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_pantry_item",
            "description": (
                "Remove a single ingredient from the pantry by name (partial match). "
                "Use purge_expired_items instead when clearing all expired items."
            ),
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
            "description": "Update remaining quantity of an item. Pass 0 to remove.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":         {"type": "string"},
                    "new_quantity": {"type": "number"},
                },
                "required": ["name", "new_quantity"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "purge_expired_items",
            "description": (
                "Delete ALL items from the pantry whose expiry_date is on or before today "
                "(expiry_date <= today), including items expiring today. "
                "Use this instead of remove_pantry_item when the user asks to clear, "
                "purge, or delete all expired items at once. One call removes everything."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

TOOL_MAP = {
    "get_pantry_items":    lambda args: get_pantry_items(),
    "get_at_risk_items":   lambda args: get_at_risk_items(**args),
    "add_pantry_item":     lambda args: add_pantry_item(**args),
    "remove_pantry_item":  lambda args: remove_pantry_item(**args),
    "update_quantity":     lambda args: update_quantity(**args),
    "purge_expired_items": lambda args: purge_expired_items(),
}


def run_agent_turn(messages) -> str:
    tool_call_count = 0
    while True:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )
        msg = resp.choices[0].message

        if not getattr(msg, "tool_calls", None):
            return msg.content or "Done."

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": msg.tool_calls,
        })

        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments or "{}")
            tool_call_count += 1
            print(f"[tool call {tool_call_count}: {fn_name}({fn_args})]")
            result = (
                TOOL_MAP[fn_name](fn_args)
                if fn_name in TOOL_MAP
                else f"ERROR: unknown tool '{fn_name}'"
            )
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, default=str),
            })


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data      = request.get_json(force=True)
    user_text = data.get("message", "").strip()
    if not user_text:
        return jsonify({"reply": "Please type a message for the Smart Pantry Chef."}), 400

    today_str = date.today().strftime("%Y-%m-%d")

    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(today=today_str)},
        {"role": "user",   "content": user_text},
    ]
    try:
        reply = run_agent_turn(conversation)
    except Exception as e:
        print("Error in run_agent_turn:", e)
        reply = "Sorry, something went wrong while thinking about your pantry."

    return jsonify({"reply": reply})


@app.route("/pantry", methods=["GET"])
def api_get_pantry():
    try:
        return jsonify({"items": get_pantry_items()})
    except Exception as e:
        print("Error fetching pantry:", e)
        return jsonify({"error": "Failed to load pantry items."}), 500


@app.route("/purge-expired", methods=["POST"])
def api_purge_expired():
    try:
        include_no_expiry = request.args.get("nulls", "false").lower() == "true"
        result = purge_expired_items(include_no_expiry=include_no_expiry)
        return jsonify(result)
    except Exception as e:
        print("Error in /purge-expired:", e)
        return jsonify({"error": f"Purge failed: {str(e)}"}), 500


@app.route("/debug-expiry", methods=["GET"])
def debug_expiry():
    today_str = date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT name, expiry_date FROM pantry ORDER BY expiry_date ASC")
    rows = cur.fetchall()
    conn.close()

    result = {
        "today":          today_str,
        "expired":        [],
        "expiring_today": [],
        "no_date":        [],
        "future":         [],
    }
    for name, expiry in rows:
        if expiry is None:
            result["no_date"].append(name)
        elif str(expiry) < today_str:
            result["expired"].append({"name": name, "expiry": str(expiry)})
        elif str(expiry) == today_str:
            result["expiring_today"].append({"name": name, "expiry": str(expiry)})
        else:
            result["future"].append({"name": name, "expiry": str(expiry)})

    return jsonify(result)


@app.route("/ocr", methods=["POST"])
def ocr_upload():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided. Use key 'image'."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type and file.content_type not in allowed:
        return jsonify({"error": f"Unsupported file type: {file.content_type}"}), 400

    try:
        img_bytes = file.read()
        Image.open(io.BytesIO(img_bytes)).verify()

        print(f"[OCR] Processing: {file.filename}")
        results = get_ocr_reader().readtext(img_bytes, detail=1)

        ocr_lines = [
            {"text": text, "confidence": round(conf, 2)}
            for (_, text, conf) in results
            if conf >= 0.3
        ]
        raw_text = "\n".join(item["text"] for item in ocr_lines)
        print(f"[OCR] Extracted:\n{raw_text}")

        if not raw_text.strip():
            return jsonify({
                "ocr_raw": [],
                "reply": "No readable text found. Please try a clearer photo."
            })

        today_str = date.today().strftime("%Y-%m-%d")

        conversation = [
            {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(today=today_str)},
            {"role": "user",   "content": OCR_PARSE_PROMPT_TEMPLATE.format(
                today=today_str,
                ocr_text=raw_text,
            )},
        ]
        reply = run_agent_turn(conversation)

        return jsonify({"ocr_raw": ocr_lines, "reply": reply})

    except Exception as e:
        print("Error in /ocr:", e)
        return jsonify({"error": f"OCR processing failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001, use_reloader=False)

    