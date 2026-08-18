<div align="center">

# ⚡ PocketAgent
### Autonomous Mobile Operating Agent with Sub-Second Groq LPU Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Groq LPU](https://img.shields.io/badge/Inference-Groq%20LPU%20(500%20tok%2Fs)-orange.svg)](https://groq.com/)
[![Dodo Payments](https://img.shields.io/badge/Payments-Dodo%20Live-green.svg)](https://dodopayments.com/)
[![Platform](https://img.shields.io/badge/Platform-Android%20%7C%20Emulators-cyan.svg)](https://developer.android.com/)
[![License](https://img.shields.io/badge/License-Commercial%20Pro-purple.svg)](https://pocketagent.ai/)

**Transform natural language goals into humanized physical actions on any Android device or PC emulator in milliseconds.**

[Live Webhook Docs](#-cloud-monetization--vercel-deployment) • [Quickstart](#-quickstart-guide) • [Architecture](#-system-architecture) • [Commercial Licensing](#-commercial-tiers--pricing)

</div>

---

## 🌟 Why PocketAgent?

Traditional mobile RPA and agent systems rely on slow Appium frameworks, fragile screen coordinates, or heavy iOS signing certificates. **PocketAgent is engineered from the ground up for speed, safety, and instant monetization:**

1. **0ms XML UI Tree Extraction**: Inspects live screen interactive nodes directly via native ADB in sub-50ms without installing any APK on the phone.
2. **Sub-Second Groq LPU Brain**: Powered by Llama-3.3-70B and Qwen models with native Function Calling for real-time decision-making.
3. **Bézier Humanized Gestures**: Generates cubic Bézier curved swipes with ease-in-out physics, random $\pm 3\text{px}$ Gaussian jitter, and natural press durations to evade anti-bot detection.
4. **Human-in-the-Loop Safety Barrier**: Automatically halts automation and requests physical confirmation for sensitive flows (payments, passcodes, transfers).
5. **Turnkey Monetization**: Built-in Dodo Payments webhook server with automated License Key generation (`PKT-XXXX-XXXX-XXXX`) and credits sync.

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph Local Client (Windows / macOS / Linux)
        UI[🖥️ Cyberpunk Control Console<br/>Flask + Vanilla JS i18n] --> Bridge[📱 Android Hardware Driver<br/>Zero-Install ADB Engine]
        UI --> Brain[🧠 Groq LPU Decision Brain<br/>ReAct Function Calling]
        UI --> Gestures[🖐️ Bézier Human Touch Engine<br/>Micro-Jitter & Curve Swipes]
        UI --> License[🔑 Client License / BYOK Module]
    end

    subgraph Physical Device / Emulator Matrix
        Bridge --> Phone[📱 Android Phone / LDPlayer / MuMu Matrix]
    end

    subgraph Cloud Serverless (Vercel / VPS)
        Dodo[💳 Dodo Payments 5 Products] -->|Payment Succeeded Webhook| Webhook[⚡ FastAPI Webhook Server]
        Webhook --> DB[(📦 License Database)]
        License -.->|Verify Key & Sync Credits| Webhook
    end
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ installed on your laptop/PC.
- An Android device with **USB Debugging enabled** (or any PC Android Emulator like LDPlayer/MuMu).

### 2. Local Setup & Execution
```bash
# Clone the repository
git clone https://github.com/your-username/pocket-agent.git
cd pocket-agent

# Install dependencies
pip install -r requirements.txt

# Launch PocketAgent Desktop Server
python app.py
```
👉 Open your browser at **`http://localhost:5899`**

---

## 📱 Android Device Connection (10-Second Setup)

1. Go to **Settings ➔ About Phone ➔ Tap 'Build Number' 7 times** to activate Developer Options.
2. Go to **Settings ➔ Developer Options ➔ Turn ON 'USB Debugging'**.
   - *Xiaomi / MIUI / HyperOS*: Also turn ON **'USB Debugging (Security Settings)'** to allow automated taps.
   - *Huawei / Honor*: Turn ON **'Allow ADB debugging in charge only mode'**.
3. Plug in the USB cable, unlock your phone, check **"Always allow from this computer"**, and tap **Allow**.
4. Set USB Mode to **"File Transfer (MTP)"**.

---

## ☁️ Cloud Monetization & Vercel Deployment

PocketAgent includes a production-ready FastAPI Webhook service ready for 1-click Vercel deployment:

### Deploy to Vercel:
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy to Vercel
vercel --prod
```

Configure your **Dodo Payments Webhook Endpoint**:
```
https://your-project.vercel.app/api/webhook/dodo
```

---

## 💳 Commercial Tiers & Pricing (Dodo Payments)

| Tier | Price | Monthly Credits | Matrix Concurrency | Checkout |
| :--- | :--- | :--- | :--- | :--- |
| **Solo Pro Monthly** | `$19.99 / mo` | 1,500 Credits | 1 Physical / Emulator | [Buy Monthly](https://checkout.dodopayments.com/buy/pdt_0NlgHtNsDlqTjbFUwWUn0?quantity=1) |
| **Solo Pro Annual** | `$149.00 / yr` | 1,500 Credits / mo | 1 Physical / Emulator | [Buy Annual (Save 38%)](https://checkout.dodopayments.com/buy/pdt_0NlgInUdPXvUMK0Rh7Gq5?quantity=1) |
| **Studio Monthly** | `$99.00 / mo` | 15,000 Credits | 5~10 Devices Matrix | [Buy Studio](https://checkout.dodopayments.com/buy/pdt_0NlgJ4QoPAHUuf5oAAPvt?quantity=1) |
| **Studio Annual** | `$699.00 / yr` | 15,000 Credits / mo | 5~10 Devices Matrix | [Buy Studio Annual (Save 41%)](https://checkout.dodopayments.com/buy/pdt_0NlgJJuf7YceGxa0yR7zr?quantity=1) |
| **Credits Refill** | `$9.90` | 1,000 Credits (No Expiry) | All Tiers | [Refill Pack](https://checkout.dodopayments.com/buy/pdt_0NlgJV8RzWqyu6jIwjP82?quantity=1) |

---

## 🛠️ Project Structure

```
pocket-agent/
├── app.py                  # Local Desktop Control Web Server (Flask)
├── agent_brain.py          # Groq LPU ReAct Decision Brain with 5 Core Tools
├── device_bridge.py        # 0ms Android Hardware Driver & Package Mapper
├── gestures.py             # Bézier Curved Gestures & Gaussian Jitter Engine
├── setup_adb.py            # Zero-Install Google Platform-Tools Downloader
├── webhook_server.py       # Dodo Payments Cloud Webhook & License Server (FastAPI)
├── config.py               # API Keys Pool, Models, and Pricing Matrix
├── api/
│   └── index.py            # Vercel Serverless Entrypoint
├── templates/
│   └── index.html          # Cyberpunk i18n Web Console (EN/ZH)
├── skills/
│   └── cardify_visual_skill.py # 4K McKinsey Cardify Deck Generator Skill
├── requirements.txt        # Python Dependencies
└── vercel.json             # Vercel Serverless Configuration
```

---

## 📄 License

PocketAgent is released under the **Commercial Pro License**. Free BYOK mode is available for personal evaluation.
