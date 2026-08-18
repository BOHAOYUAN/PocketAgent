import os

# PocketAgent Configuration Matrix
# Load keys safely from environment or .env file

def get_groq_keys():
    env_keys = os.getenv("GROQ_API_KEYS", "")
    if env_keys:
        return [k.strip() for k in env_keys.split(",") if k.strip()]
    single_key = os.getenv("GROQ_API_KEY", "")
    if single_key:
        return [single_key.strip()]
    
    # Fallback to local .env if available
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GROQ_API_KEYS="):
                    raw = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return [k.strip() for k in raw.split(",") if k.strip()]
                elif line.startswith("GROQ_API_KEY="):
                    return [line.split("=", 1)[1].strip().strip('"').strip("'")]

    return ["gsk_placeholder_key_for_evaluation"]

GROQ_API_KEYS = get_groq_keys()

# Dodo Payments Live Checkout Links
PAYMENT_LINKS = {
    "solo_pro_monthly": "https://checkout.dodopayments.com/buy/pdt_0NlgHtNsDlqTjbFUwWUn0?quantity=1",
    "solo_pro_annual": "https://checkout.dodopayments.com/buy/pdt_0NlgInUdPXvUMK0Rh7Gq5?quantity=1",
    "studio_monthly": "https://checkout.dodopayments.com/buy/pdt_0NlgJ4QoPAHUuf5oAAPvt?quantity=1",
    "studio_annual": "https://checkout.dodopayments.com/buy/pdt_0NlgJJuf7YceGxa0yR7zr?quantity=1",
    "credits_topup": "https://checkout.dodopayments.com/buy/pdt_0NlgJV8RzWqyu6jIwjP82?quantity=1",
}

# Groq LPU Models (High-Speed Function Calling)
DEFAULT_MODEL = "qwen/qwen3.6-27b"
BACKUP_MODEL = "openai/gpt-oss-120b"

# Default Local Server Port
SERVER_PORT = 5899
