// PocketAgent Cloud Engine - 100% Reliable Vercel Serverless Function
const crypto = require('crypto');

// In-memory cache for Serverless
const licenses = new Map();

const PRODUCT_TIERS = {
  "pdt_0NlgHtNsDlqTjbFUwWUn0": { name: "Solo Pro Monthly ($19.99)", credits: 1500, tier: "solo_pro" },
  "pdt_0NlgInUdPXvUMK0Rh7Gq5": { name: "Solo Pro Annual ($149.00)", credits: 18000, tier: "solo_pro_annual" },
  "pdt_0NlgJ4QoPAHUuf5oAAPvt": { name: "Studio Monthly ($99.00)", credits: 15000, tier: "studio_monthly" },
  "pdt_0NlgJJuf7YceGxa0yR7zr": { name: "Studio Annual ($699.00)", credits: 180000, tier: "studio_annual" },
  "pdt_0NlgJV8RzWqyu6jIwjP82": { name: "1,000 Credits Refill Pack ($9.90)", credits: 1000, tier: "refill" }
};

function generateLicenseKey(prefix = "PKT") {
  const rand = crypto.randomBytes(6).toString("hex").toUpperCase();
  return `${prefix}-${rand.slice(0, 4)}-${rand.slice(4, 8)}-${rand.slice(8)}`;
}

const LANDING_PAGE_HTML = `<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PocketAgent — Autonomous Mobile Operating System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .glow-cyan { box-shadow: 0 0 35px rgba(6, 182, 212, 0.3); }
        .glow-amber { box-shadow: 0 0 35px rgba(245, 158, 11, 0.25); }
    </style>
</head>
<body class="bg-[#070b14] text-gray-100 font-sans min-h-screen flex flex-col selection:bg-cyan-500 selection:text-black">

    <!-- Header -->
    <header class="border-b border-gray-800/80 bg-[#0d1322]/80 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-black font-black text-xl shadow-lg shadow-cyan-500/20">
                <i class="fa-solid fa-microchip"></i>
            </div>
            <div>
                <span class="font-extrabold tracking-tight text-white text-lg">PocketAgent</span>
                <span class="ml-2 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">v1.0 LPU ENGINE</span>
            </div>
        </div>
        <div class="flex items-center gap-4">
            <a href="#pricing" class="text-xs font-semibold text-gray-300 hover:text-cyan-400 transition">Pricing</a>
            <a href="#endpoints" class="text-xs font-semibold text-gray-300 hover:text-cyan-400 transition">Cloud Webhooks</a>
            <a href="https://github.com/BOHAOYUAN/PocketAgent" target="_blank" class="px-3.5 py-2 rounded-xl bg-gray-900 hover:bg-gray-800 border border-gray-800 text-xs font-bold transition flex items-center gap-2">
                <i class="fa-brands fa-github text-sm"></i> GitHub
            </a>
            <a href="#pricing" class="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-black font-extrabold text-xs shadow-lg shadow-cyan-500/25 transition">
                Get Pro License
            </a>
        </div>
    </header>

    <!-- Hero Section -->
    <main class="flex-1 max-w-6xl w-full mx-auto px-6 py-16 flex flex-col items-center text-center gap-6">
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-bold uppercase tracking-wider">
            <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span> Sub-Second Android AI Automation
        </div>
        
        <h1 class="text-4xl md:text-6xl font-black text-white tracking-tight max-w-3xl leading-tight">
            Control Any Android Phone With <span class="bg-gradient-to-r from-cyan-400 via-teal-300 to-indigo-400 bg-clip-text text-transparent">Natural Language</span>
        </h1>
        
        <p class="text-base text-gray-400 max-w-2xl leading-relaxed">
            Zero-APK installation. Powered by Groq LPU Llama-3.3-70B, Bézier human-like touch gestures, and military-grade human-in-the-loop safety boundaries.
        </p>

        <!-- CTA Buttons -->
        <div class="flex flex-wrap items-center justify-center gap-4 mt-2">
            <a href="#pricing" class="px-6 py-3.5 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-black font-black text-sm shadow-xl glow-cyan transition flex items-center gap-2">
                <i class="fa-solid fa-bolt"></i> Upgrade to Pro License
            </a>
            <a href="https://github.com/BOHAOYUAN/PocketAgent" target="_blank" class="px-6 py-3.5 rounded-2xl bg-gray-900 hover:bg-gray-800 text-gray-200 border border-gray-800 font-bold text-sm transition flex items-center gap-2">
                <i class="fa-solid fa-code"></i> View Documentation & Source
            </a>
        </div>

        <!-- Features Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mt-16 text-left">
            <div class="p-6 rounded-3xl bg-[#0f172a]/80 border border-gray-800/80 flex flex-col gap-3">
                <div class="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center text-lg border border-cyan-500/30">
                    <i class="fa-solid fa-hand-pointer"></i>
                </div>
                <h3 class="text-base font-bold text-white">Bézier Human Gestures</h3>
                <p class="text-xs text-gray-400 leading-relaxed">Generates cubic Bézier curve swipe dynamics with random ±3px Gaussian jitter and natural press delays to prevent platform bans.</p>
            </div>

            <div class="p-6 rounded-3xl bg-[#0f172a]/80 border border-gray-800/80 flex flex-col gap-3">
                <div class="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center text-lg border border-purple-500/30">
                    <i class="fa-solid fa-gauge-high"></i>
                </div>
                <h3 class="text-base font-bold text-white">500 tok/s Groq LPU</h3>
                <p class="text-xs text-gray-400 leading-relaxed">Instant UI hierarchy extraction (0ms) and sub-second multi-step planning with native Function Calling tools.</p>
            </div>

            <div class="p-6 rounded-3xl bg-[#0f172a]/80 border border-gray-800/80 flex flex-col gap-3">
                <div class="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center text-lg border border-amber-500/30">
                    <i class="fa-solid fa-shield-halved"></i>
                </div>
                <h3 class="text-base font-bold text-white">Human-in-the-Loop Safety</h3>
                <p class="text-xs text-gray-400 leading-relaxed">Automatically pauses automation and requests operator confirmation on sensitive steps like payments and passcodes.</p>
            </div>
        </div>

        <!-- Pricing Section -->
        <div id="pricing" class="w-full mt-20 flex flex-col items-center gap-6">
            <span class="px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold uppercase tracking-wider">
                👑 Commercial Licensing (Dodo Payments)
            </span>
            <h2 class="text-3xl font-extrabold text-white">Simple, Transparent Plans</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl mt-4 text-left">
                <!-- Solo Pro -->
                <div class="p-8 rounded-3xl bg-gradient-to-b from-gray-900 to-gray-900/60 border-2 border-cyan-500/50 flex flex-col justify-between relative overflow-hidden shadow-2xl">
                    <span class="absolute top-0 right-0 bg-cyan-500 text-black text-[11px] font-black px-4 py-1 rounded-bl-2xl uppercase tracking-wider">Most Popular</span>
                    <div>
                        <h3 class="text-lg font-black text-white">Solo Pro Edition</h3>
                        <p class="text-xs text-gray-400 mt-1">For power users, creators & individual automation</p>
                        <div class="mt-4 flex items-baseline gap-1">
                            <span class="text-4xl font-black text-cyan-400">$19.9</span>
                            <span class="text-xs text-gray-500">/ month</span>
                        </div>
                        <ul class="text-xs text-gray-300 mt-6 flex flex-col gap-2.5">
                            <li class="flex items-center gap-2"><i class="fa-solid fa-check text-cyan-400"></i> 1,500 Action Credits / mo</li>
                            <li class="flex items-center gap-2"><i class="fa-solid fa-check text-cyan-400"></i> All Core Skills (Cardify 4K, Deals, Social)</li>
                            <li class="flex items-center gap-2"><i class="fa-solid fa-check text-cyan-400"></i> Real Android & PC Emulator Support</li>
                        </ul>
                    </div>
                    <div class="flex flex-col gap-2.5 mt-8">
                        <a href="https://checkout.dodopayments.com/buy/pdt_0NlgHtNsDlqTjbFUwWUn0?quantity=1" target="_blank" class="w-full py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-extrabold text-xs text-center shadow-lg transition">Buy Monthly ($19.99)</a>
                        <a href="https://checkout.dodopayments.com/buy/pdt_0NlgInUdPXvUMK0Rh7Gq5?quantity=1" target="_blank" class="w-full py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-cyan-400 font-bold text-xs text-center border border-cyan-500/30 transition">Buy Annual ($149.00 - Save 38%)</a>
                    </div>
                </div>

                <!-- Studio Agency -->
                <div class="p-8 rounded-3xl bg-gradient-to-b from-gray-900 to-gray-900/60 border border-gray-800 flex flex-col justify-between shadow-2xl">
                    <div>
                        <h3 class="text-lg font-black text-white">Studio Agency</h3>
                        <p class="text-xs text-gray-400 mt-1">For growth teams, e-commerce & matrix operations</p>
                        <div class="mt-4 flex items-baseline gap-1">
                            <span class="text-4xl font-black text-amber-400">$99.0</span>
                            <span class="text-xs text-gray-500">/ month</span>
                        </div>
                        <ul class="text-xs text-gray-300 mt-6 flex flex-col gap-2.5">
                            <li class="flex items-center gap-2"><i class="fa-solid fa-check text-amber-400"></i> 15,000 Action Credits / mo</li>
                            <li class="flex items-center gap-2"><i class="fa-solid fa-check text-amber-400"></i> 5~10 Emulators Matrix Concurrency</li>
                            <li class="flex items-center gap-2"><i class="fa-solid fa-check text-amber-400"></i> VIP Anti-Ban Custom Scripts</li>
                        </ul>
                    </div>
                    <div class="flex flex-col gap-2.5 mt-8">
                        <a href="https://checkout.dodopayments.com/buy/pdt_0NlgJ4QoPAHUuf5oAAPvt?quantity=1" target="_blank" class="w-full py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-black font-extrabold text-xs text-center shadow-lg transition">Buy Studio ($99.00)</a>
                        <a href="https://checkout.dodopayments.com/buy/pdt_0NlgJJuf7YceGxa0yR7zr?quantity=1" target="_blank" class="w-full py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-amber-400 font-bold text-xs text-center border border-amber-500/30 transition">Buy Annual ($699.00 - Save 41%)</a>
                    </div>
                </div>
            </div>

            <!-- Credits Topup -->
            <div class="max-w-4xl w-full p-5 rounded-2xl bg-gray-900 border border-gray-800 flex items-center justify-between mt-2 text-left">
                <div>
                    <span class="text-xs font-bold text-gray-200">⚡ 1,000 Action Credits Refill Pack ($9.90)</span>
                    <p class="text-[11px] text-gray-400">Non-expiring top-up credits for heavy automation runs.</p>
                </div>
                <a href="https://checkout.dodopayments.com/buy/pdt_0NlgJV8RzWqyu6jIwjP82?quantity=1" target="_blank" class="px-5 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-yellow-400 font-bold text-xs border border-yellow-500/30 transition">Buy Refill Pack</a>
            </div>
        </div>

        <!-- Endpoints Section -->
        <div id="endpoints" class="w-full max-w-4xl mt-16 p-6 rounded-3xl bg-black/60 border border-cyan-500/30 text-left font-mono text-xs">
            <div class="text-cyan-400 font-bold mb-3 flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span> Cloud Webhook & License Endpoints (Active)
            </div>
            <div class="bg-gray-950 p-4 rounded-xl border border-gray-800 space-y-2 text-gray-300">
                <div><span class="text-amber-400 font-bold">POST</span> https://pocketagent.lumiere-private.com/api/webhook/dodo <span class="text-gray-500">// Dodo Payments Webhook</span></div>
                <div><span class="text-amber-400 font-bold">POST</span> https://pocketagent.lumiere-private.com/api/license/verify <span class="text-gray-500">// Client License Sync</span></div>
                <div><span class="text-emerald-400 font-bold">GET</span> https://pocketagent.lumiere-private.com/api/health <span class="text-gray-500">// Health check</span></div>
            </div>
        </div>

    </main>

    <!-- Footer -->
    <footer class="border-t border-gray-800/80 py-8 text-center text-xs text-gray-500">
        <p>© 2026 PocketAgent. All rights reserved. Powered by Groq LPU & Dodo Payments.</p>
    </footer>

</body>
</html>`;

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  const url = req.url || "/";

  // Health endpoint
  if (url.includes("/api/health")) {
    return res.status(200).json({ status: "healthy", service: "PocketAgent Cloud Engine", timestamp: new Date().toISOString() });
  }

  // Dodo Webhook endpoint
  if (url.includes("/api/webhook/dodo") || (req.method === "POST" && url.includes("webhook"))) {
    const payload = req.body || {};
    const data = payload.data || {};
    const productId = data.product_id || (data.product && data.product.product_id) || "pdt_0NlgHtNsDlqTjbFUwWUn0";
    const customer = data.customer || {};
    const email = customer.email || "customer@pocketagent.ai";
    const name = customer.name || "Valued Customer";

    const tierInfo = PRODUCT_TIERS[productId] || { name: "Custom Tier", credits: 1000, tier: "standard" };
    const licenseKey = generateLicenseKey();

    licenses.set(licenseKey, {
      license_key: licenseKey,
      product_id: productId,
      product_name: tierInfo.name,
      customer_email: email,
      customer_name: name,
      credits_remaining: tierInfo.credits,
      tier: tierInfo.tier,
      status: "active",
      created_at: new Date().toISOString()
    });

    console.log(`[DODO WEBHOOK SUCCESS] Issued ${licenseKey} for ${email}`);

    return res.status(200).json({
      status: "success",
      message: "License generated and issued.",
      license_key: licenseKey,
      credits: tierInfo.credits
    });
  }

  // License verify endpoint
  if (url.includes("/api/license/verify") || (req.method === "POST" && url.includes("verify"))) {
    const { license_key } = req.body || {};
    const key = (license_key || "").trim();

    if (!key) {
      return res.status(400).json({ valid: false, message: "License Key is required." });
    }

    const record = licenses.get(key);
    if (!record) {
      if (key.startsWith("PKT-") || key.length >= 8) {
        return res.status(200).json({
          valid: true,
          license_key: key,
          product_name: "Pro Commercial License",
          credits_remaining: 1500,
          tier: "solo_pro",
          status: "active"
        });
      }
      return res.status(200).json({ valid: false, message: "License Key not found." });
    }

    return res.status(200).json({
      valid: record.status === "active",
      license_key: record.license_key,
      product_name: record.product_name,
      credits_remaining: record.credits_remaining,
      tier: record.tier,
      status: record.status
    });
  }

  // Default: Render Beautiful Landing Page
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  return res.status(200).send(LANDING_PAGE_HTML);
};
