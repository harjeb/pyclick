import math
import numpy as np
import random

class DistanceBasedTiming:
    """
    基于移动距离的动态点密度和时间间隔算法
    """
    
    def __init__(self):
        # 基于真实数据的距离-密度关系
        self.distance_density_map = {
            # (min_distance, max_distance): (base_density, density_variation)
            (0, 100): (0.45, 0.08),      # 短距离: 高密度
            (100, 300): (0.35, 0.06),    # 中距离: 中等密度  
            (300, 600): (0.25, 0.05),    # 长距离: 较低密度
            (600, float('inf')): (0.15, 0.03)  # 超长距离: 低密度
        }
        
        # 基于真实手动数据优化的时间间隔模式（毫秒）
        self.step_interval_map = {
            # (步长范围): (基础间隔ms, 变化范围ms, 权重)
            # 更细分的范围和更大的随机变化
            (0, 0.5): (15.0, 12.0, 0.10),     # 静止点: 15±12ms
            (0.5, 1.5): (13.0, 10.0, 0.15),   # 极小移动: 13±10ms
            (1.5, 2.5): (11.0, 9.0, 0.20),    # 微小移动: 11±9ms
            (2.5, 4.0): (9.0, 7.0, 0.25),     # 小移动: 9±7ms
            (4.0, 6.0): (8.0, 6.0, 0.15),     # 中小移动: 8±6ms
            (6.0, 10.0): (7.0, 5.0, 0.10),    # 中等移动: 7±5ms
            (10.0, 20.0): (6.0, 4.0, 0.04),   # 较大移动: 6±4ms
            (20.0, 100.0): (5.0, 3.0, 0.01)   # 大移动: 5±3ms
        }
        
        # 思考延迟参数 - 更自然的随机延迟
        self.thinking_probability = 0.08  # 8%概率出现思考延迟  
        self.thinking_min = 150.0  # 最小延迟150ms
        self.thinking_max = 250.0  # 最大延迟250ms
    
    def calculate_optimal_point_count(self, total_distance):
        """
        根据总移动距离计算最优点数
        """
        # 确定密度范围
        density = 0.25  # 默认密度
        for (min_dist, max_dist), (base_density, variation) in self.distance_density_map.items():
            if min_dist <= total_distance < max_dist:
                # 添加随机变化
                density = base_density + random.uniform(-variation, variation)
                break
        
        # 确保合理的点数范围
        point_count = max(20, int(total_distance * density))
        point_count = min(point_count, int(total_distance * 0.8))  # 最多不超过0.8点/像素
        
        return point_count
    
    def get_interval_for_step_distance(self, step_distance):
        """
        根据单步距离获取时间间隔
        """
        # 先检查思考延迟 - 只对真正的停顿点（距离<0.5像素）应用
        if step_distance < 0.5 and random.random() < self.thinking_probability:
            return random.uniform(self.thinking_min, self.thinking_max) / 1000.0
        
        # 查找对应的间隔范围
        for (min_step, max_step), (base_interval, variation, weight) in self.step_interval_map.items():
            if min_step <= step_distance < max_step:
                # 使用更随机的分布，避免固定值集中
                if variation > 8:  # 高变化范围 - 使用均匀分布
                    interval = random.uniform(base_interval - variation/2, base_interval + variation/2)
                    interval = max(3.0, interval)  # 最小3ms
                else:  # 低变化范围 - 使用正态分布
                    interval = np.random.normal(base_interval, variation * 1.5)  # 增加1.5倍变化
                    interval = max(3.0, min(50.0, interval))  # 限制在3-50ms
                
                # 添加额外的随机微调，破坏规律性
                interval *= random.uniform(0.8, 1.2)  # ±20%随机调整
                
                return interval / 1000.0
        
        # 默认返回 - 添加随机化避免固定值
        return random.uniform(0.008, 0.015)  # 8-15ms随机
    
    def generate_intervals_for_points(self, points):
        """
        为给定的点序列生成时间间隔
        """
        if len(points) < 2:
            return []
        
        intervals = []
        for i in range(1, len(points)):
            prev_point = points[i-1]
            curr_point = points[i]
            
            # 计算单步距离
            step_distance = math.sqrt(
                (curr_point[0] - prev_point[0])**2 + 
                (curr_point[1] - prev_point[1])**2
            )
            
            interval = self.get_interval_for_step_distance(step_distance)
            intervals.append(interval)
        
        return intervals
    
    def get_timing_stats(self, total_distance, sample_count=1000):
        """
        获取指定距离的时间间隔统计信息
        """
        point_count = self.calculate_optimal_point_count(total_distance)
        
        # 模拟步长分布（简化）
        avg_step = total_distance / max(1, point_count - 1)
        intervals = []
        
        for _ in range(sample_count):
            # 模拟变化的步长
            step_variation = random.uniform(0.5, 2.0)
            step_distance = avg_step * step_variation
            interval = self.get_interval_for_step_distance(step_distance) * 1000
            intervals.append(interval)
        
        intervals = np.array(intervals)
        return {
            'total_distance': total_distance,
            'optimal_points': point_count,
            'point_density': point_count / total_distance,
            'intervals': {
                'mean': intervals.mean(),
                'median': np.median(intervals),
                'std': intervals.std(),
                'min': intervals.min(),
                'max': intervals.max()
            }
        }
    
    def set_thinking_parameters(self, probability, min_ms, max_ms):
        """设置思考延迟参数"""
        self.thinking_probability = max(0.0, min(1.0, probability))
        self.thinking_min = max(0.0, min_ms)
        self.thinking_max = max(self.thinking_min, max_ms)
        
    def adjust_density_for_distance(self, total_distance, density_factor=1.0):
        """
        调整特定距离的点密度因子
        density_factor: 1.0=默认, >1.0=更密集, <1.0=更稀疏
        """
        for distance_range in self.distance_density_map:
            min_dist, max_dist = distance_range
            if min_dist <= total_distance < max_dist:
                base_density, variation = self.distance_density_map[distance_range]
                self.distance_density_map[distance_range] = (
                    base_density * density_factor, 
                    variation
                )
                break