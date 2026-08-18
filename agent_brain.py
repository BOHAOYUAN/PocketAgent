import requests
import json
import time
from config import GROQ_API_KEYS, DEFAULT_MODEL, BACKUP_MODEL

class AgentBrain:
    def __init__(self, custom_api_key=None):
        self.api_keys = [custom_api_key] if custom_api_key else GROQ_API_KEYS
        self.current_key_idx = 0
        self.model = DEFAULT_MODEL
        self.action_history = []

    def _get_active_key(self):
        return self.api_keys[self.current_key_idx % len(self.api_keys)]

    def _rotate_key(self):
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
        print(f"[ROTATE] Rotating to Groq API Key #{self.current_key_idx + 1}")

    def plan_next_step(self, user_goal, screen_elements, history=None):
        """
        基于当前手机屏幕 UI 树，调用 Groq Llama-3.3-70B 原生 Tool-Use 进行单步决策
        """
        # 将 UI 树元素精炼成易读的文本提示词，包含确切的 Bounds
        elements_summary = []
        for eid, info in list(screen_elements.items())[:65]: # 截取前 65 个可见互动元素
            label = info.get("label", "")
            elem_class = info.get("class", "")
            bounds = info.get("bounds", "")
            clickable_tag = " [可点击]" if info.get("clickable") else ""
            
            if label or info.get("clickable"):
                elements_summary.append(f"- ID: {eid} | 文本/描述: \"{label}\" | 类型: {elem_class}{clickable_tag} | 坐标Bounds: {bounds}")

        elements_text = "\n".join(elements_summary) if elements_summary else "当前屏幕未探测到可见交互元素。"

        # 遵循严谨的 5 大核心工具定义与安全边界规范
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "open_app",
                    "description": "通过指定包名或应用名称，打开手机上的特定 App。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string", "description": "应用的中文名称或包名，例如 '微信', 'com.xingin.xhs'"}
                        },
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "click_element",
                    "description": "模拟人类手指，点击屏幕 UI 树中指定坐标的中心点。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "bounds": {"type": "string", "description": "UI 树中元素的 bounds 属性坐标，格式如 '[100,200][300,400]'。系统会自动计算中心点点击。"},
                            "reason": {"type": "string", "description": "点击此元素的理由，用于日志记录"}
                        },
                        "required": ["bounds"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "input_text",
                    "description": "在屏幕当前带有光标（默认在输入框）的位置，输入指定的文本内容。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "需要输入的字符串内容"}
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "swipe_screen",
                    "description": "执行滑动操作，通常用于翻页列表或关闭弹窗。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "direction": {"type": "string", "enum": ["up", "down", "left", "right"], "description": "滑动的方向"},
                            "duration": {"type": "integer", "description": "滑动持续时长（毫秒），默认 500ms，可以稍长以模拟人类"}
                        },
                        "required": ["direction"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "human_confirm",
                    "description": "遇到安全边界（支付、输入密码、验证码、或高危操作）时调用。暂停自动化，把控制权交还给用户。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "向用户展示的暂停原因，例如 '即将执行转账，请确认是否继续...'"}
                        },
                        "required": ["message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "finish_task",
                    "description": "当用户的核心目标已完全达成时调用此工具声明任务结束。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "向用户汇报的完成总结"}
                        },
                        "required": ["message"]
                    }
                }
            }
        ]

        system_prompt = """# 角色与目标
你是一个专门用于自动化操控 Android 手机的 AI Agent。
你的核心任务是将用户的“自然语言指令”拆解为一系列连续的“手机物理操作步骤”。
你拥有对当前手机屏幕 UI 树（包含所有可见元素的文本、描述和坐标范围 Bounds）的实时读取权限。

# 执行规则 (必须严格遵守)
1. **基于 UI 树决策**：所有点击操作必须基于当前提供的 UI 树元素坐标范围（Bounds）的中心点。绝对不能凭空捏造坐标。
2. **单步执行与反馈**：每次操作只返回 ONE (一个) 具体的动作。当你执行完动作后，系统将自动为你抓取新的屏幕 UI 树供你进行下一步决策。如果任务完成，请调用 finish_task 工具。
3. **防风控机制**：在执行点击或滑动时，使用拟人化的动作，不要机械式地极速点击。
4. **异常处理**：如果 UI 树中找不到用户指定的目标（例如“点击设置”但当前屏幕没有设置按钮），请先尝试寻找返回键或向上滑动，或者调用 finish_task 向用户反馈“当前屏幕未找到该目标”。
5. **安全与边界防护（重中之重）**：
   - 如果当前屏幕出现支付密码框、银行 App、或包含“转账”、“验证码”、“输入支付密码”、“确认付款”等字眼，或者你推断当前即将执行转账/付款/敏感权限操作，**必须调用 human_confirm 工具立即暂停自动化，并请求用户人工干预确认**，严禁 AI 代替用户进行资产高风险操作。"""

        recent_history = history[-4:] if history else []
        history_str = json.dumps(recent_history, ensure_ascii=False, indent=2) if recent_history else "无（刚开始执行）"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""【用户核心目标】: {user_goal}

【前序已执行操作历史】:
{history_str}

【当前手机屏幕 UI 树元素列表】:
{elements_text}

请根据用户目标和当前屏幕状态，选择唯一最合适的工具调用进行下一步操作。"""}
        ]

        # 调用 Groq API，支持自动轮换与 Rate-Limit 容灾
        for attempt in range(len(self.api_keys) * 2):
            api_key = self._get_active_key()
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
                "temperature": 0.1,
                "max_tokens": 512
            }

            try:
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=8)
                if res.status_code == 200:
                    data = res.json()
                    choice = data["choices"][0]["message"]
                    tool_calls = choice.get("tool_calls", [])
                    if tool_calls:
                        tc = tool_calls[0]
                        func_name = tc["function"]["name"]
                        func_args = json.loads(tc["function"]["arguments"])
                        return {
                            "tool": func_name,
                            "args": func_args,
                            "raw": choice
                        }
                    else:
                        content = choice.get("content", "").strip()
                        if "已完成" in content or "success" in content.lower():
                            return {
                                "tool": "finish_task",
                                "args": {"message": content}
                            }
                        return {
                            "tool": "finish_task",
                            "args": {"message": content if content else "步骤已执行完毕。"}
                        }
                elif res.status_code in [429, 401]:
                    print(f"Groq API Key (index {self.current_key_idx}) status {res.status_code}. Rotating key...")
                    self._rotate_key()
                else:
                    print(f"Groq API Error {res.status_code}: {res.text}")
                    self._rotate_key()
            except Exception as e:
                print(f"Network error calling Groq: {e}")
                self._rotate_key()

            time.sleep(0.5)

        return {"tool": "error", "args": {"message": "Groq API 连接失败或所有 API 密钥达到上限。"}}
