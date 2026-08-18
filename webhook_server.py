import os
import sqlite3
import secrets
import time
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="PocketAgent Monetization & License Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "licenses.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
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

init_db()

# Dodo Product Mapping Matrix
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

@app.get("/")
def root():
    return {"status": "online", "service": "PocketAgent License & Webhook Server"}

@app.post("/api/webhook/dodo")
async def dodo_webhook(request: Request):
    """
    Webhook handler for Dodo Payments live callbacks
    Event: payment.succeeded / subscription.active
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("type") or payload.get("event") or "payment.succeeded"
    data = payload.get("data", {})
    
    # Extract details
    product_id = data.get("product_id") or data.get("product", {}).get("product_id") or "pdt_0NlgHtNsDlqTjbFUwWUn0"
    customer = data.get("customer", {})
    email = customer.get("email", "customer@pocketagent.ai")
    name = customer.get("name", "Valued Customer")

    tier_info = PRODUCT_TIERS.get(product_id, {"name": "Custom Tier", "credits": 1000, "tier": "standard"})
    
    license_key = generate_license_key()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO licenses (license_key, product_id, product_name, customer_email, customer_name, credits_remaining, tier, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
    """, (license_key, product_id, tier_info["name"], email, name, tier_info["credits"], tier_info["tier"]))
    conn.commit()
    conn.close()

    print(f"[DODO PAYMENT SUCCESS] Issued License: {license_key} for {email} ({tier_info['name']}) with {tier_info['credits']} credits.")

    return {
        "status": "success",
        "message": "License generated and issued.",
        "license_key": license_key,
        "credits": tier_info["credits"]
    }

class LicenseVerifyRequest(BaseModel):
    license_key: str

@app.post("/api/license/verify")
def verify_license(req: LicenseVerifyRequest):
    key = req.license_key.strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT license_key, product_name, credits_remaining, tier, status FROM licenses WHERE license_key = ?", (key,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"valid": False, "message": "License Key not found."}

    lic_key, prod_name, credits, tier, status = row
    if status != "active":
        return {"valid": False, "message": f"License is currently {status}."}

    return {
        "valid": True,
        "license_key": lic_key,
        "product_name": prod_name,
        "credits_remaining": credits,
        "tier": tier,
        "status": status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
