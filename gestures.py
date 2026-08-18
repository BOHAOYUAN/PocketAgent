import random
import math
import time
import re

class HumanizedGestureEngine:
    """
    拟人化物理触控手势算法引擎
    - 三次贝塞尔曲线滑动 (带加减速缓动)
    - 高斯微颤点击 (±3px 随机抖动)
    - 拟人按压微延迟 (110ms ~ 160ms)
    - 彻底规避 App 机械行为风控检测
    """

    @staticmethod
    def parse_bounds(bounds_str):
        """
        解析 UI 树 bounds 字符串，例如 '[100,200][300,400]'
        返回 bounds 字典
        """
        if not bounds_str:
            return None
        match = re.findall(r"\[(\d+),(\d+)\]", str(bounds_str))
        if match and len(match) == 2:
            x1, y1 = int(match[0][0]), int(match[0][1])
            x2, y2 = int(match[1][0]), int(match[1][1])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            return {
                "x1": x1, "y1": y1,
                "x2": x2, "y2": y2,
                "width": x2 - x1,
                "height": y2 - y1,
                "cx": cx, "cy": cy
            }
        return None

    @staticmethod
    def get_jittered_click_point(bounds_info):
        """
        在元素中心点附近生成带高斯分布的微颤点击坐标，并保证绝不出界
        """
        cx = bounds_info["cx"]
        cy = bounds_info["cy"]
        w = max(bounds_info["width"], 10)
        h = max(bounds_info["height"], 10)

        # 最大允许偏移量不超过长宽的 15%，且在 1~4 像素之间
        max_jx = min(4, max(1, int(w * 0.15)))
        max_jy = min(4, max(1, int(h * 0.15)))

        # 高斯随机微颤
        jx = int(random.gauss(0, max_jx / 2))
        jy = int(random.gauss(0, max_jy / 2))

        # 钳制在安全范围内
        jx = max(-max_jx, min(max_jx, jx))
        jy = max(-max_jy, min(max_jy, jy))

        target_x = max(bounds_info["x1"] + 2, min(bounds_info["x2"] - 2, cx + jx))
        target_y = max(bounds_info["y1"] + 2, min(bounds_info["y2"] - 2, cy + jy))

        # 拟人按压时长 (110ms ~ 170ms)
        press_duration = random.randint(110, 165)
        return target_x, target_y, press_duration

    @staticmethod
    def generate_bezier_swipe_points(start_x, start_y, end_x, end_y, num_points=10):
        """
        生成拟人化的三次贝塞尔曲线滑动路径点序列 (模拟人手划屏时的弧度与加减速)
        """
        dx = end_x - start_x
        dy = end_y - start_y
        dist = math.hypot(dx, dy)

        # 随机弯曲偏离度 (根据滑动距离产生弧线偏移)
        arc_offset = random.uniform(-0.12, 0.12) * dist

        # 控制点 1
        ctrl1_x = start_x + dx * 0.25 - dy * (arc_offset / dist if dist else 0) + random.uniform(-4, 4)
        ctrl1_y = start_y + dy * 0.25 + dx * (arc_offset / dist if dist else 0) + random.uniform(-4, 4)

        # 控制点 2
        ctrl2_x = start_x + dx * 0.75 - dy * (arc_offset * 0.5 / dist if dist else 0) + random.uniform(-3, 3)
        ctrl2_y = start_y + dy * 0.75 + dx * (arc_offset * 0.5 / dist if dist else 0) + random.uniform(-3, 3)

        points = []
        for i in range(num_points + 1):
            s = i / num_points
            # 缓动函数 Ease-In-Out (两头慢中间快)
            t = (1 - math.cos(s * math.pi)) / 2

            u = 1 - t
            tt = t * t
            uu = u * u
            uuu = uu * u
            ttt = tt * t

            px = uuu * start_x + 3 * uu * t * ctrl1_x + 3 * u * tt * ctrl2_x + ttt * end_x
            py = uuu * start_y + 3 * uu * t * ctrl1_y + 3 * u * tt * ctrl2_y + ttt * end_y

            points.append((int(px), int(py)))

        return points
