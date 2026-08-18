import os
import sqlite3
import secrets
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

DB_PATH = "/tmp/licenses.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT UNIQUE NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                customer_email TEXT,
                customer_name TEXT,
                credits_remaining INTEGER NOT NULL,
                tier TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR]: {e}")

PRODUCT_TIERS = {
    "pdt_0NlgHtNsDlqTjbFUwWUn0": {"name": "Solo Pro Monthly ($19.99)", "credits": 1500, "tier": "solo_pro"},
    "pdt_0NlgInUdPXvUMK0Rh7Gq5": {"name": "Solo Pro Annual ($149.00)", "credits": 18000, "tier": "solo_pro_annual"},
    "pdt_0NlgJ4QoPAHUuf5oAAPvt": {"name": "Studio Monthly ($99.00)", "credits": 15000, "tier": "studio_monthly"},
    "pdt_0NlgJJuf7YceGxa0yR7zr": {"name": "Studio Annual ($699.00)", "credits": 180000, "tier": "studio_annual"},
    "pdt_0NlgJV8RzWqyu6jIwjP82": {"name": "1,000 Credits Refill Pack ($9.90)", "credits": 1000, "tier": "refill"},
}

def generate_license_key(prefix="PKT"):
    random_part = secrets.token_hex(6).upper()
    return f"{prefix}-{random_part[:4]}-{random_part[4:8]}-{random_part[8:]}"

LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PocketAgent Cloud Monetization Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#090d16] text-gray-100 flex items-center justify-center min-h-screen font-sans">
    <div class="max-w-md w-full bg-gray-900/90 border border-cyan-500/30 rounded-3xl p-8 text-center shadow-2xl shadow-cyan-500/10">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-black font-black text-2xl mx-auto shadow-lg shadow-cyan-500/30">
            ⚡
        </div>
        <h1 class="text-xl font-black text-white mt-4 tracking-tight">PocketAgent Cloud Engine</h1>
        <p class="text-xs text-gray-400 mt-1">Global Webhook & License Authentication Service</p>
        <div class="mt-6 p-4 rounded-2xl bg-black/60 border border-gray-800 text-left text-xs font-mono">
            <div class="text-cyan-400 font-bold mb-2">⚡ Active Cloud Endpoints:</div>
            <div class="text-emerald-400 flex items-center gap-1.5 mb-1"><span class="w-2 h-2 rounded-full bg-emerald-400"></span> POST /api/webhook/dodo</div>
            <div class="text-emerald-400 flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-emerald-400"></span> POST /api/license/verify</div>
        </div>
        <div class="mt-6 text-[11px] text-gray-500 font-mono">
            Running on Vercel Serverless Edge • 100% Operational
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
@app.route("/api", methods=["GET"])
@app.route("/api/index", methods=["GET"])
def root():
    return render_template_string(LANDING_HTML)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "PocketAgent Cloud Webhook & License API"})

@app.route("/api/webhook/dodo", methods=["POST"])
def dodo_webhook():
    init_db()
    try:
        payload = request.get_json(force=True, silent=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON payload"}), 400

    data = payload.get("data", {})
    product_id = data.get("product_id") or data.get("product", {}).get("product_id") or "pdt_0NlgHtNsDlqTjbFUwWUn0"
    customer = data.get("customer", {})
    email = customer.get("email", "customer@pocketagent.ai")
    name = customer.get("name", "Valued Customer")

    tier_info = PRODUCT_TIERS.get(product_id, {"name": "Custom Tier", "credits": 1000, "tier": "standard"})
    license_key = generate_license_key()
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO licenses (license_key, product_id, product_name, customer_email, customer_name, credits_remaining, tier, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
        """, (license_key, product_id, tier_info["name"], email, name, tier_info["credits"], tier_info["tier"]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB INSERT ERROR]: {e}")

    return jsonify({
        "status": "success",
        "message": "License generated and issued.",
        "license_key": license_key,
        "credits": tier_info["credits"]
    })

@app.route("/api/license/verify", methods=["POST"])
def verify_license():
    init_db()
    data = request.get_json(force=True, silent=True) or {}
    key = data.get("license_key", "").strip()
    if not key:
        return jsonify({"valid": False, "message": "License Key is required."}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT license_key, product_name, credits_remaining, tier, status FROM licenses WHERE license_key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
    except Exception as e:
        return jsonify({"valid": False, "message": f"Database error: {e}"})

    if not row:
        return jsonify({"valid": False, "message": "License Key not found."})

    lic_key, prod_name, credits, tier, status = row
    if status != "active":
        return jsonify({"valid": False, "message": f"License is currently {status}."})

    return jsonify({
        "valid": True,
        "license_key": lic_key,
        "product_name": prod_name,
        "credits_remaining": credits,
        "tier": tier,
        "status": status
    })

if __name__ == "__main__":
    app.run(port=8000)
