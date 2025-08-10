import pyautogui
import time
import random
from pyclick.humancurve import HumanCurve
from pyclick.human_timing import HumanTiming
from pyclick.distance_based_timing import DistanceBasedTiming

def setup_pyautogui():
    # Any duration less than this is rounded to 0.0 to instantly move the mouse.
    pyautogui.MINIMUM_DURATION = 0  # Default: 0.1
    # Minimal number of seconds to sleep between mouse moves.
    pyautogui.MINIMUM_SLEEP = 0  # Default: 0.05
    # The number of seconds to pause after EVERY public function call.
    pyautogui.PAUSE = 0  # Disable PyAutoGUI pause, use algorithm timing only

setup_pyautogui()

class HumanClicker():
    def __init__(self, use_human_timing=True, use_distance_based=True):
        self.use_human_timing = use_human_timing
        self.use_distance_based = use_distance_based
        
        # 选择时间间隔生成器
        if use_distance_based:
            self.timing_generator = DistanceBasedTiming() if use_human_timing else None
        else:
            self.timing_generator = HumanTiming() if use_human_timing else None

    def move(self, toPoint, duration=2, humanCurve=None):
        fromPoint = pyautogui.position()
        if not humanCurve:
            # 创建曲线时传递distance_based参数
            humanCurve = HumanCurve(fromPoint, toPoint, use_distance_based=self.use_distance_based)

        if self.use_human_timing and self.timing_generator:
            if self.use_distance_based:
                # 使用基于距离的间隔时间
                intervals = self.timing_generator.generate_intervals_for_points(humanCurve.points)
            else:
                # 使用原有的固定间隔生成
                intervals = self.timing_generator.get_intervals(len(humanCurve.points))
            
            for i, point in enumerate(humanCurve.points):
                # 为长间隔添加微小随机抖动，模拟人类微颤
                if i < len(intervals) and intervals[i] > 0.02:  # 间隔>20ms时添加抖动
                    jitter_x = random.uniform(-1, 1)  # ±1像素抖动
                    jitter_y = random.uniform(-1, 1)
                    jittered_point = (int(point[0] + jitter_x), int(point[1] + jitter_y))
                    pyautogui.moveTo(jittered_point)
                else:
                    pyautogui.moveTo(point)
                
                if i < len(intervals):
                    time.sleep(intervals[i])
        else:
            # 使用固定间隔（原有方式）
            pyautogui.PAUSE = duration / len(humanCurve.points) if duration > 0 else 0.008
            for point in humanCurve.points:
                pyautogui.moveTo(point)
                
    def set_thinking_probability(self, probability):
        """设置思考延迟概率 (0.0-1.0)"""
        if self.timing_generator:
            if self.use_distance_based:
                self.timing_generator.set_thinking_parameters(probability, 
                    self.timing_generator.thinking_min, self.timing_generator.thinking_max)
            else:
                self.timing_generator.set_thinking_probability(probability)
    
    def set_thinking_range(self, min_ms, max_ms):
        """设置思考延迟范围（毫秒）"""
        if self.timing_generator:
            if self.use_distance_based:
                self.timing_generator.set_thinking_parameters(
                    self.timing_generator.thinking_probability, min_ms, max_ms)
            else:
                self.timing_generator.set_thinking_range(min_ms, max_ms)
    
    def enable_human_timing(self, enabled=True):
        """启用/禁用拟人化时间间隔"""
        self.use_human_timing = enabled
        if enabled and not self.timing_generator:
            if self.use_distance_based:
                self.timing_generator = DistanceBasedTiming()
            else:
                self.timing_generator = HumanTiming()
    
    def enable_distance_based_timing(self, enabled=True):
        """启用/禁用基于距离的时间间隔"""
        self.use_distance_based = enabled
        if self.use_human_timing:
            if enabled:
                self.timing_generator = DistanceBasedTiming()
            else:
                self.timing_generator = HumanTiming()
    
    def get_timing_stats(self, total_distance=200, sample_count=1000):
        """获取时间间隔统计信息（用于调试）"""
        if self.timing_generator:
            if self.use_distance_based:
                return self.timing_generator.get_timing_stats(total_distance, sample_count)
            else:
                return self.timing_generator.get_stats(sample_count)
        return None

    def click(self):
        pyautogui.click()





