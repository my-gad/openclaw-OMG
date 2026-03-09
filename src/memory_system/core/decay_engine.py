#!/usr/bin/env python3
"""
Decay Engine - 记忆衰减引擎

基于神经科学的遗忘曲线实现记忆自动衰减。
"""

import math
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

from memory_system.core.memory_manager import MemoryRecord, MemoryType


@dataclass
class DecayConfig:
    """衰减配置"""
    # 衰减率（每日）
    fact_decay: float = 0.008      # 半衰期 ~87 天
    belief_decay: float = 0.07     # 半衰期 ~10 天
    summary_decay: float = 0.025   # 半衰期 ~28 天
    event_decay: float = 0.15      # 半衰期 ~5 天
    
    # 权重阈值
    archive_threshold: float = 0.3   # 低于此值归档
    delete_threshold: float = 0.1    # 低于此值删除


class DecayEngine:
    """
    衰减引擎
    
    实现基于时间的记忆权重衰减。
    """
    
    def __init__(self, config: Optional[DecayConfig] = None):
        self.config = config or DecayConfig()
    
    def _get_decay_rate(self, memory_type: MemoryType) -> float:
        """获取对应类型的衰减率"""
        rates = {
            MemoryType.FACT: self.config.fact_decay,
            MemoryType.BELIEF: self.config.belief_decay,
            MemoryType.SUMMARY: self.config.summary_decay,
            MemoryType.EVENT: self.config.event_decay,
        }
        return rates.get(memory_type, self.config.fact_decay)
    
    def calculate_decay(self, record: MemoryRecord, current_time: Optional[float] = None) -> float:
        """
        计算当前权重
        
        公式：新权重 = 原始置信度 × e^(-衰减率 × 天数)
        """
        current_time = current_time or time.time()
        days_elapsed = (current_time - record.timestamp) / (24 * 3600)
        
        decay_rate = self._get_decay_rate(record.memory_type)
        decay_factor = math.exp(-decay_rate * days_elapsed)
        
        # 访问会增强记忆（简单实现：每次访问增加 10%）
        access_boost = 1.0 + (record.access_count * 0.1)
        
        new_weight = record.confidence * decay_factor * access_boost
        return min(new_weight, 1.0)  # 上限为 1.0
    
    def apply_decay(
        self,
        records: List[MemoryRecord],
        current_time: Optional[float] = None
    ) -> List[Dict[str, any]]:
        """
        对一批记忆应用衰减
        
        返回：[(record, new_weight, action), ...]
        action: 'keep' | 'archive' | 'delete'
        """
        results = []
        
        for record in records:
            new_weight = self.calculate_decay(record, current_time)
            
            if new_weight < self.config.delete_threshold:
                action = 'delete'
            elif new_weight < self.config.archive_threshold:
                action = 'archive'
            else:
                action = 'keep'
            
            results.append({
                'record': record,
                'weight': new_weight,
                'action': action,
            })
        
        return results
    
    def get_half_life(self, memory_type: MemoryType) -> float:
        """获取半衰期（天）"""
        decay_rate = self._get_decay_rate(memory_type)
        return math.log(2) / decay_rate
    
    def get_decay_summary(self, records: List[MemoryRecord]) -> Dict[str, any]:
        """获取衰减统计摘要"""
        summary = {
            'total': len(records),
            'keep': 0,
            'archive': 0,
            'delete': 0,
            'avg_weight': 0.0,
        }
        
        total_weight = 0.0
        results = self.apply_decay(records)
        
        for result in results:
            action = result['action']
            summary[action] += 1
            total_weight += result['weight']
        
        if records:
            summary['avg_weight'] = total_weight / len(records)
        
        return summary
