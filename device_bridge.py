import subprocess
import xml.etree.ElementTree as ET
import re
import time
import random
import os
import shutil
import requests
import json
import base64
from gestures import HumanizedGestureEngine

APP_PACKAGE_MAP = {
    # Social & Messaging
    "微信": "com.tencent.mm",
    "wechat": "com.tencent.mm",
    "qq": "com.tencent.mobileqq",
    "微博": "com.sina.weibo",
    "weibo": "com.sina.weibo",
    "推特": "com.twitter.android",
    "twitter": "com.twitter.android",
    "x": "com.twitter.android",
    "telegram": "org.telegram.messenger",
    "whatsapp": "com.whatsapp",
    "instagram": "com.instagram.android",
    "facebook": "com.facebook.katana",
    
    # Community & Media
    "小红书": "com.xingin.xhs",
    "red": "com.xingin.xhs",
    "抖音": "com.ss.android.ugc.aweme",
    "tiktok": "com.zhiliaoapp.musically",
    "快手": "com.smile.gifmaker",
    "哔哩哔哩": "tv.danmaku.bili",
    "bilibili": "tv.danmaku.bili",
    "知乎": "com.zhihu.android",
    "youtube": "com.google.android.youtube",
    
    # E-commerce & Utilities
    "淘宝": "com.taobao.taobao",
    "taobao": "com.taobao.taobao",
    "京东": "com.jingdong.app.mall",
    "jd": "com.jingdong.app.mall",
    "拼多多": "com.xunmeng.pinduoduo",
    "pinduoduo": "com.xunmeng.pinduoduo",
    "美团": "com.sankuai.meituan",
    "meituan": "com.sankuai.meituan",
    "饿了么": "me.ele",
    "支付宝": "com.eg.android.AlipayGphone",
    "alipay": "com.eg.android.AlipayGphone",
    
    # System Tools
    "设置": "com.android.settings",
    "settings": "com.android.settings",
    "相机": "com.android.camera",
    "camera": "com.android.camera",
    "相册": "com.android.gallery3d",
    "gallery": "com.google.android.apps.photos",
    "chrome": "com.android.chrome",
    "浏览器": "com.android.chrome",
    "browser": "com.android.browser",
    "文件管理": "com.android.documentsui",
}

def get_adb_binary():
    """Locate bundled or system ADB executable with zero-install guarantee"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bundled_adb = os.path.join(base_dir, "bin", "platform-tools", "adb.exe")
    if os.path.exists(bundled_adb):
        return bundled_adb
    
    system_adb = shutil.which("adb")
    if system_adb:
        return system_adb
    
    # Fallback to setup_adb if needed
    try:
        from setup_adb import download_and_extract_adb
        return download_and_extract_adb()
    except Exception:
        return "adb"

class DeviceBridge:
    def __init__(self, platform="android", device_id=None):
        self.platform = platform.lower()
        self.device_id = device_id
        self.last_elements = {}
        self.screen_width = 1080
        self.screen_height = 2400
        self.adb_bin = get_adb_binary()
        self._update_screen_resolution()

    def _get_adb_prefix(self):
        cmd = [self.adb_bin]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        return cmd

    def _update_screen_resolution(self):
        """Detect actual screen resolution via ADB"""
        try:
            cmd = self._get_adb_prefix() + ["shell", "wm", "size"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
            match = re.search(r"Physical size:\s*(\d+)x(\d+)", res.stdout)
            if match:
                self.screen_width = int(match.group(1))
                self.screen_height = int(match.group(2))
        except Exception:
            pass

    def list_devices(self):
        """List all connected Android physical devices and emulators with detailed status"""
        devices = []
        try:
            res = subprocess.run([self.adb_bin, "devices", "-l"], capture_output=True, text=True, timeout=5)
            lines = res.stdout.strip().split("\n")[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    dev_id = parts[0]
                    status_raw = parts[1]
                    
                    # Determine type
                    dev_type = "Emulator" if ("emulator" in dev_id or "127.0.0.1" in dev_id or "localhost" in dev_id) else "Physical Android"
                    
                    # Extract model if present
                    model = "Android Device"
                    for p in parts[2:]:
                        if p.startswith("model:"):
                            model = p.replace("model:", "").replace("_", " ")

                    # Status mapping
                    status = "online"
                    msg = "Ready"
                    if status_raw == "unauthorized":
                        status = "unauthorized"
                        msg = "Please unlock phone & tap 'Allow USB Debugging' on screen"
                    elif status_raw == "offline":
                        status = "offline"
                        msg = "Device is offline / sleeping"

                    devices.append({
                        "id": dev_id,
                        "model": model,
                        "platform": "android",
                        "type": dev_type,
                        "status": status,
                        "message": msg
                    })
        except Exception as e:
            print(f"ADB list devices error: {e}")

        return devices

    def capture_screenshot(self, output_path="static/screenshot.png"):
        """Capture live device screenshot at full speed"""
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        cmd = self._get_adb_prefix() + ["exec-out", "screencap", "-p"]
        try:
            res = subprocess.run(cmd, capture_output=True, timeout=5)
            if res.returncode == 0 and len(res.stdout) > 1000:
                with open(output_path, "wb") as f:
                    f.write(res.stdout)
                return output_path
        except Exception as e:
            print(f"Android screenshot error: {e}")
        return None

    def dump_ui_hierarchy(self):
        """
        0ms-level XML UI tree extraction and structure parsing.
        Extracts visible text, resource-id, content-desc, clickable state and exact bounds.
        """
        elements = {}
        cmd = self._get_adb_prefix() + ["exec-out", "uiautomator", "dump", "/dev/tty"]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=8)
            xml_data = res.stdout.strip()
            if "<?xml" in xml_data:
                xml_data = xml_data[xml_data.find("<?xml"):]
                root = ET.fromstring(xml_data)
                node_idx = 1
                for node in root.iter("node"):
                    text = node.attrib.get("text", "").strip()
                    desc = node.attrib.get("content-desc", "").strip()
                    res_id = node.attrib.get("resource-id", "").strip()
                    bounds_str = node.attrib.get("bounds", "")
                    clickable = node.attrib.get("clickable", "false") == "true"
                    focusable = node.attrib.get("focusable", "false") == "true"
                    scrollable = node.attrib.get("scrollable", "false") == "true"
                    
                    bounds_info = HumanizedGestureEngine.parse_bounds(bounds_str)
                    if bounds_info and bounds_info["width"] > 0 and bounds_info["height"] > 0:
                        if text or desc or clickable or focusable or scrollable:
                            label = text if text else desc
                            if not label and res_id:
                                label = res_id.split("/")[-1]
                            
                            elem_id = f"node_{node_idx}"
                            elements[elem_id] = {
                                "id": elem_id,
                                "label": label if label else f"Element_{node_idx}",
                                "text": text,
                                "desc": desc,
                                "class": node.attrib.get("class", "").split(".")[-1],
                                "clickable": clickable,
                                "bounds": bounds_str,
                                "center": [bounds_info["cx"], bounds_info["cy"]],
                                "width": bounds_info["width"],
                                "height": bounds_info["height"]
                            }
                            node_idx += 1
        except Exception as e:
            print(f"Android UI dump error: {e}")

        self.last_elements = elements
        return elements

    def click_element(self, bounds, reason=""):
        """
        Click on element bounds center using Bézier / Gaussian jitter and humanized duration
        """
        bounds_info = HumanizedGestureEngine.parse_bounds(bounds)
        if not bounds_info:
            print(f"[Click Error] Invalid bounds string: {bounds}")
            return False

        target_x, target_y, duration = HumanizedGestureEngine.get_jittered_click_point(bounds_info)
        print(f"[Click] Bounds: {bounds} -> Target: ({target_x}, {target_y}), duration: {duration}ms | Reason: {reason}")

        cmd = self._get_adb_prefix() + [
            "shell", "input", "swipe",
            str(target_x), str(target_y),
            str(target_x), str(target_y),
            str(duration)
        ]
        try:
            subprocess.run(cmd, timeout=4)
            time.sleep(random.uniform(0.35, 0.7))
            return True
        except Exception as e:
            print(f"Click execution error: {e}")
            return False

    def input_text(self, text):
        """
        Input text naturally. Handles English, Numbers and Chinese UTF-8 characters.
        """
        print(f"[Input Text] '{text}'")
        has_unicode = any(ord(c) > 127 for c in text)

        if has_unicode:
            # Clipboard Paste Keyevent
            try:
                cmd_clip = self._get_adb_prefix() + ["shell", "cmd", "clipboard", "set", "text", text]
                res = subprocess.run(cmd_clip, capture_output=True, timeout=3)
                if res.returncode == 0:
                    time.sleep(0.15)
                    cmd_paste = self._get_adb_prefix() + ["shell", "input", "keyevent", "279"]
                    subprocess.run(cmd_paste, timeout=3)
                    time.sleep(0.3)
                    return True
            except Exception:
                pass

            try:
                b64_str = base64.b64encode(text.encode("utf-8")).decode("utf-8")
                cmd_b64 = self._get_adb_prefix() + ["shell", "am", "broadcast", "-a", "ADB_INPUT_B64", "--es", "msg", b64_str]
                subprocess.run(cmd_b64, timeout=3)
            except Exception:
                pass
        else:
            escaped = text.replace(" ", "%s").replace("&", "\&").replace("'", "\\'").replace('"', '\\"')
            cmd = self._get_adb_prefix() + ["shell", "input", "text", escaped]
            subprocess.run(cmd, timeout=4)

        time.sleep(random.uniform(0.2, 0.5))
        return True

    def swipe_screen(self, direction="up", duration=500):
        """
        Perform smooth human-like Bézier curved swipe
        """
        print(f"[Swipe] Direction: {direction}, Duration: {duration}ms")
        cx = self.screen_width // 2 + random.randint(-15, 15)
        
        if direction == "up":
            start_x, start_y = cx, int(self.screen_height * 0.72)
            end_x, end_y = cx + random.randint(-20, 20), int(self.screen_height * 0.28)
        elif direction == "down":
            start_x, start_y = cx, int(self.screen_height * 0.28)
            end_x, end_y = cx + random.randint(-20, 20), int(self.screen_height * 0.72)
        elif direction == "left":
            start_x, start_y = int(self.screen_width * 0.85), self.screen_height // 2
            end_x, end_y = int(self.screen_width * 0.15), self.screen_height // 2 + random.randint(-15, 15)
        elif direction == "right":
            start_x, start_y = int(self.screen_width * 0.15), self.screen_height // 2
            end_x, end_y = int(self.screen_width * 0.85), self.screen_height // 2 + random.randint(-15, 15)
        else:
            start_x, start_y = cx, int(self.screen_height * 0.7)
            end_x, end_y = cx, int(self.screen_height * 0.3)

        swipe_duration = max(300, min(1200, duration + random.randint(-40, 40)))
        cmd = self._get_adb_prefix() + [
            "shell", "input", "swipe",
            str(start_x), str(start_y),
            str(end_x), str(end_y),
            str(swipe_duration)
        ]
        try:
            subprocess.run(cmd, timeout=5)
            time.sleep(random.uniform(0.4, 0.8))
            return True
        except Exception as e:
            print(f"Swipe execution error: {e}")
            return False

    def open_app(self, app_name):
        """
        Open app by name or package identifier
        """
        clean_name = app_name.strip().lower()
        package_name = APP_PACKAGE_MAP.get(clean_name, app_name.strip())

        print(f"[Open App] '{app_name}' -> Package: '{package_name}'")
        cmd = self._get_adb_prefix() + [
            "shell", "monkey", "-p", package_name,
            "-c", "android.intent.category.LAUNCHER", "1"
        ]
        try:
            subprocess.run(cmd, timeout=5)
            time.sleep(random.uniform(1.2, 1.8))
            return True
        except Exception as e:
            print(f"Open app error: {e}")
            return False
