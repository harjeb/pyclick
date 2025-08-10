import random
import numpy as np

class HumanTiming:
    """
    基于真实手动移动数据的拟人化时间间隔生成器
    """
    
    def __init__(self):
        # 基于真实手动数据优化的间隔配置
        self.normal_intervals = {
            'weight': 85.0,  # 减少固定模式权重
            'min': 15.0,     # 增加最小间隔
            'max': 45.0,     # 增加最大间隔
            'mean': 25.0,    # 提高平均间隔
            'std': 8.0       # 增加变化范围
        }
        
        self.medium_intervals = {
            'weight': 8.0,     # 增加中等间隔权重
            'min': 45.0,       # 提高最小值
            'max': 80.0        # 提高最大值
        }
        
        self.long_intervals = {
            'weight': 4.0,     # 增加长间隔权重
            'min': 80.0,
            'max': 150.0
        }
        
        self.extra_long_intervals = {
            'weight': 2.0,     # 减少权重避免过于频繁
            'min': 150.0,
            'max': 300.0
        }
        
        self.very_long_intervals = {
            'weight': 1.0,     # 减少极长间隔权重
            'min': 300.0,
            'max': 800.0      # 增加最大延迟
        }
        
        # 思考延迟参数
        self.thinking_probability = 0.08  # 8%概率，更真实的思考延迟
        self.thinking_min = 120.0  # 120ms
        self.thinking_max = 500.0  # 500ms
    
    def get_interval(self):
        """
        获取下一个时间间隔（毫秒）
        """
        # 先检查是否触发思考延迟
        if random.random() < self.thinking_probability:
            return random.uniform(self.thinking_min, self.thinking_max) / 1000.0
        
        # 根据权重选择间隔类型
        rand = random.uniform(0, 100)
        
        if rand < self.normal_intervals['weight']:
            # 95.5% - 正常间隔，使用正态分布模拟真实数据
            interval = np.random.normal(
                self.normal_intervals['mean'], 
                self.normal_intervals['std']
            )
            # 限制在合理范围内
            interval = max(self.normal_intervals['min'], 
                         min(self.normal_intervals['max'], interval))
        elif rand < self.normal_intervals['weight'] + self.medium_intervals['weight']:
            # 1.8% - 中等间隔
            interval = random.uniform(
                self.medium_intervals['min'],
                self.medium_intervals['max']
            )
        elif rand < (self.normal_intervals['weight'] + 
                    self.medium_intervals['weight'] + 
                    self.long_intervals['weight']):
            # 0.7% - 长间隔
            interval = random.uniform(
                self.long_intervals['min'],
                self.long_intervals['max']
            )
        elif rand < (self.normal_intervals['weight'] + 
                    self.medium_intervals['weight'] + 
                    self.long_intervals['weight'] +
                    self.extra_long_intervals['weight']):
            # 0.7% - 超长间隔
            interval = random.uniform(
                self.extra_long_intervals['min'],
                self.extra_long_intervals['max']
            )
        else:
            # 1.3% - 极长间隔
            interval = random.uniform(
                self.very_long_intervals['min'],
                self.very_long_intervals['max']
            )
        
        # 转换为秒
        return interval / 1000.0
    
    def get_intervals(self, count):
        """
        获取指定数量的时间间隔列表
        """
        return [self.get_interval() for _ in range(count)]
    
    def set_thinking_probability(self, probability):
        """
        设置思考延迟的概率 (0.0 - 1.0)
        """
        self.thinking_probability = max(0.0, min(1.0, probability))
    
    def set_thinking_range(self, min_ms, max_ms):
        """
        设置思考延迟的时间范围（毫秒）
        """
        self.thinking_min = max(0.0, min_ms)
        self.thinking_max = max(self.thinking_min, max_ms)
        
    def get_stats(self, sample_count=1000):
        """
        获取间隔统计信息（用于测试）
        """
        intervals = [self.get_interval() * 1000 for _ in range(sample_count)]
        return {
            'count': len(intervals),
            'mean': np.mean(intervals),
            'median': np.median(intervals),
            'std': np.std(intervals),
            'min': min(intervals),
            'max': max(intervals),
            'percentiles': {
                '50': np.percentile(intervals, 50),
                '75': np.percentile(intervals, 75),
                '90': np.percentile(intervals, 90),
                '95': np.percentile(intervals, 95)
            }
        }