import os
import json
import time
import threading
from flask import Flask, render_template, request, jsonify, send_file, Response
from config import GROQ_API_KEYS, PAYMENT_LINKS, SERVER_PORT
from device_bridge import DeviceBridge
from agent_brain import AgentBrain
from skills.cardify_visual_skill import CardifyVisualSkill

app = Flask(__name__, static_folder="static", template_folder="templates")
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Global Runtime State
active_bridge = DeviceBridge(platform="android")
active_brain = AgentBrain()
is_running = False
is_paused_for_human = False
human_prompt_message = ""
current_task = None
task_logs = []
user_credits = 50 # Default trial credits
is_pro_user = False
human_continue_event = threading.Event()
active_target_bounds = None # For live highlight overlay

@app.route("/")
def index():
    return render_template("index.html", payment_links=PAYMENT_LINKS)

@app.route("/api/devices", methods=["GET"])
def api_devices():
    devices = active_bridge.list_devices()
    return jsonify({
        "devices": devices,
        "current_platform": active_bridge.platform,
        "adb_path": active_bridge.adb_bin,
        "screen_size": [active_bridge.screen_width, active_bridge.screen_height]
    })

@app.route("/api/select_device", methods=["POST"])
def api_select_device():
    global active_bridge
    data = request.json or {}
    device_id = data.get("device_id")
    active_bridge = DeviceBridge(platform="android", device_id=device_id)
    return jsonify({"status": "success", "device_id": device_id})

@app.route("/api/screenshot", methods=["GET"])
def api_screenshot():
    shot_path = active_bridge.capture_screenshot("static/screenshot.png")
    if shot_path and os.path.exists(shot_path):
        return send_file(shot_path, mimetype="image/png")
    return send_file("static/placeholder.png", mimetype="image/png") if os.path.exists("static/placeholder.png") else jsonify({"error": "No device connected"})

@app.route("/api/live_stream")
def api_live_stream():
    """MJPEG continuous low-latency live mirror stream"""
    def generate_frames():
        while True:
            shot_path = active_bridge.capture_screenshot("static/stream_frame.png")
            if shot_path and os.path.exists(shot_path):
                with open(shot_path, "rb") as f:
                    frame = f.read()
                yield (b"--frame\r\n"
                       b"Content-Type: image/png\r\n\r\n" + frame + b"\r\n")
            time.sleep(0.4) # Smooth low-overhead refresh
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/api/inspect_ui", methods=["GET"])
def api_inspect_ui():
    elements = active_bridge.dump_ui_hierarchy()
    return jsonify({"count": len(elements), "elements": elements, "screen_size": [active_bridge.screen_width, active_bridge.screen_height]})

@app.route("/api/execute_task", methods=["POST"])
def api_execute_task():
    global is_running, is_paused_for_human, human_prompt_message, current_task, task_logs, user_credits, active_target_bounds
    if is_running:
        return jsonify({"status": "busy", "message": "An autonomous task is already running."})

    data = request.json or {}
    goal = data.get("goal", "").strip()
    byok_key = data.get("byok_key", "").strip()
    
    if not goal:
        return jsonify({"status": "error", "message": "Task goal prompt cannot be empty."})

    if not is_pro_user and not byok_key and user_credits <= 0:
        return jsonify({"status": "exhausted", "message": "Action credits exhausted. Please upgrade to Pro or provide your self-hosted BYOK Groq Key."})

    brain = AgentBrain(custom_api_key=byok_key) if byok_key else active_brain
    
    task_logs = []
    is_running = True
    is_paused_for_human = False
    human_prompt_message = ""
    current_task = goal
    active_target_bounds = None
    human_continue_event.clear()

    def run_agent_loop():
        global is_running, is_paused_for_human, human_prompt_message, user_credits, active_target_bounds
        history = []
        max_steps = 25

        task_logs.append({
            "step": 0,
            "type": "start",
            "message": f"🚀 PocketAgent Initialized | Mission Goal: '{goal}'"
        })

        for step in range(1, max_steps + 1):
            if not is_running:
                task_logs.append({"step": step, "type": "abort", "message": "Mission aborted by operator."})
                break

            # 1. Capture UI Tree & Snapshot
            task_logs.append({
                "step": step,
                "type": "thinking",
                "message": f"Step {step}: Inspecting live screen UI hierarchy & elements..."
            })
            elements = active_bridge.dump_ui_hierarchy()
            active_bridge.capture_screenshot(f"static/step_{step}.png")

            # 2. Call Groq Decision Brain
            decision = brain.plan_next_step(goal, elements, history)
            tool_name = decision.get("tool")
            args = decision.get("args", {})

            # 3. Handle Tool Execution
            if tool_name == "open_app":
                app_name = args.get("app_name", "")
                active_bridge.open_app(app_name)
                task_logs.append({
                    "step": step,
                    "type": "action",
                    "tool": "open_app",
                    "app_name": app_name,
                    "message": f"📲 Launching Application: [{app_name}]"
                })
                history.append(f"Opened app {app_name}")

            elif tool_name == "click_element":
                bounds = args.get("bounds", "")
                reason = args.get("reason", "")
                active_target_bounds = bounds
                active_bridge.click_element(bounds, reason)
                task_logs.append({
                    "step": step,
                    "type": "action",
                    "tool": "click_element",
                    "bounds": bounds,
                    "reason": reason,
                    "message": f"👆 Humanized Click on {bounds} | Reason: {reason}"
                })
                history.append(f"Clicked {bounds} ({reason})")

            elif tool_name == "input_text":
                text = args.get("text", "")
                active_bridge.input_text(text)
                task_logs.append({
                    "step": step,
                    "type": "action",
                    "tool": "input_text",
                    "text": text,
                    "message": f"⌨️ Typing Text: “{text}”"
                })
                history.append(f"Typed text '{text}'")

            elif tool_name == "swipe_screen":
                direction = args.get("direction", "up")
                duration = int(args.get("duration", 500))
                active_bridge.swipe_screen(direction, duration)
                task_logs.append({
                    "step": step,
                    "type": "action",
                    "tool": "swipe_screen",
                    "direction": direction,
                    "duration": duration,
                    "message": f"📜 Bézier Smooth Swipe: Swiping {direction.upper()} ({duration}ms)"
                })
                history.append(f"Swiped {direction}")

            elif tool_name == "human_confirm":
                msg = args.get("message", "Sensitive action encountered (payment/password/confirmation). Please confirm on phone screen!")
                is_paused_for_human = True
                human_prompt_message = msg
                task_logs.append({
                    "step": step,
                    "type": "human_confirm",
                    "tool": "human_confirm",
                    "message": f"🛡️ [HUMAN-IN-THE-LOOP REQUIRED]: {msg}"
                })
                human_continue_event.clear()
                is_confirmed = human_continue_event.wait(timeout=180) # 3 min timeout
                is_paused_for_human = False
                if not is_confirmed or not is_running:
                    task_logs.append({
                        "step": step,
                        "type": "abort",
                        "message": "Human confirmation timeout or aborted."
                    })
                    break
                else:
                    task_logs.append({
                        "step": step,
                        "type": "resume",
                        "message": "✅ Human confirmation received. AI resuming next steps."
                    })
                    history.append("Operator confirmed sensitive step.")

            elif tool_name == "finish_task":
                msg = args.get("message", "Task successfully completed.")
                task_logs.append({
                    "step": step,
                    "type": "success",
                    "tool": "finish_task",
                    "message": f"🎉 Mission Accomplished! {msg}"
                })
                break

            else:
                err_msg = args.get("message", "Unknown action state")
                task_logs.append({"step": step, "type": "error", "message": f"⚠️ Execution paused: {err_msg}"})
                break

            # Deduct credit
            if not byok_key and not is_pro_user:
                user_credits = max(0, user_credits - 1)

            time.sleep(1.0)

        is_running = False
        is_paused_for_human = False
        active_target_bounds = None

    threading.Thread(target=run_agent_loop, daemon=True).start()
    return jsonify({"status": "started", "goal": goal})

@app.route("/api/human_confirm_action", methods=["POST"])
def api_human_confirm_action():
    global human_continue_event, is_running
    data = request.json or {}
    action = data.get("action", "continue")
    if action == "continue":
        human_continue_event.set()
        return jsonify({"status": "resumed"})
    else:
        is_running = False
        human_continue_event.set()
        return jsonify({"status": "aborted"})

@app.route("/api/task_status", methods=["GET"])
def api_task_status():
    return jsonify({
        "is_running": is_running,
        "is_paused_for_human": is_paused_for_human,
        "human_prompt_message": human_prompt_message,
        "current_task": current_task,
        "logs": task_logs,
        "credits": user_credits,
        "is_pro": is_pro_user,
        "active_bounds": active_target_bounds
    })

@app.route("/api/stop_task", methods=["POST"])
def api_stop_task():
    global is_running, human_continue_event
    is_running = False
    human_continue_event.set()
    return jsonify({"status": "stopped"})

@app.route("/api/activate_license", methods=["POST"])
def api_activate_license():
    global is_pro_user, user_credits
    data = request.json or {}
    key = data.get("key", "").strip()
    if len(key) >= 6:
        is_pro_user = True
        user_credits = 99999
        return jsonify({"status": "success", "message": "Pro License activated! Unlimited VIP credits unlocked."})
    return jsonify({"status": "error", "message": "Invalid License Key format."})

if __name__ == "__main__":
    print(f"[POCKETAGENT] Desktop Server online at http://localhost:{SERVER_PORT}")
    app.run(host="0.0.0.0", port=SERVER_PORT, debug=False)
