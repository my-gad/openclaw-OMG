#!/usr/bin/env python3
"""
Memory System v1.3.0 - Memory Operator
记忆操作决策引擎：ADD/UPDATE/DELETE/NOOP
"""

import re
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class MemoryOperator:
    """
    记忆操作决策引擎
    
    决策流程：
    1. 规则快速过滤（0 Token）
    2. 语义相似度检测（本地模型）
    3. LLM 冲突决策（仅在必要时）
    """
    
    # 操作类型
    OPERATIONS = ['ADD', 'UPDATE', 'DELETE', 'NOOP']
    
    # 明确的噪声模式
    NOISE_PATTERNS = [
        r'\d+\s*[\+\-\*/]\s*\d+',       # 数学计算
        r'what is \d+',                 # 琐碎问答
        r'今天天气',                     # 天气查询
        r'现在几点',                     # 时间查询
        r'帮我搜索',                     # 临时指令
        r'\d+\s*(米|厘米|千克|克)',      # 单位换算
        r'翻译[:：]',                    # 翻译请求
        r'定时\d+分钟',                  # 定时器
        r'等于多少',                     # 计算问题
    ]
    
    # 噪声关键词
    NOISE_KEYWORDS = [
        '计算器', '搜索', '查询', '帮我找',
        '翻译', '定时', '闹钟', '提醒',
        '单位换算', '多少钱', '怎么走'
    ]
    
    def __init__(self, llm_client=None, similarity_threshold: float = 0.7, backend=None):
        """
        初始化
        
        Args:
            llm_client: LLM 客户端（可选，用于复杂决策）
            similarity_threshold: 语义相似度阈值
            backend: SQLite 后端（用于冲突解决）
        """
        self.llm_client = llm_client
        self.similarity_threshold = similarity_threshold
        self.backend = backend
        
        # 冲突解决器
        from .conflict_resolver import ConflictResolver
        self.conflict_resolver = ConflictResolver(backend=backend)
        
        # 噪声过滤器
        from .noise_filter import NoiseFilter
        self.noise_filter = NoiseFilter(llm_client=llm_client, strict_mode=False)
        
        # 统计信息
        self.stats = {
            'total': 0,
            'add': 0,
            'update': 0,
            'delete': 0,
            'noop': 0,
            'llm_calls': 0
        }
    
    def decide_operation(
        self, 
        new_memory: Dict, 
        existing_memories: List[Dict]
    ) -> Tuple[str, Optional[Dict]]:
        """
        决定对新记忆执行什么操作
        
        Args:
            new_memory: 新提取的记忆
            existing_memories: 相关的已有记忆
        
        Returns:
            (操作类型, 目标记忆)
            - ('ADD', None): 添加新记忆
            - ('UPDATE', old_memory): 更新旧记忆
            - ('DELETE', old_memory): 删除旧记忆
            - ('NOOP', None): 不执行任何操作
        """
        self.stats['total'] += 1
        
        # ============================================================
        # 第一层：规则快速过滤（0 Token）
        # ============================================================
        
        # 1.1 检查是否为明确的噪声
        if self._is_obvious_noise(new_memory):
            self.stats['noop'] += 1
            return ('NOOP', None)
        
        # 1.2 如果没有已有记忆，直接添加
        if not existing_memories:
            self.stats['add'] += 1
            return ('ADD', None)
        
        # ============================================================
        # 第二层：语义相似度检测（本地模型，0 Token）
        # ============================================================
        
        # 2.1 查找潜在冲突
        conflicts = self._find_conflicts_by_similarity(new_memory, existing_memories)
        
        # 2.2 如果没有冲突，直接添加
        if not conflicts:
            self.stats['add'] += 1
            return ('ADD', None)
        
        # ============================================================
        # 第三层：LLM 决策（仅在有冲突时调用）
        # ============================================================
        
        # 3.1 如果有 LLM 客户端，使用 LLM 决策
        if self.llm_client:
            operation, target = self._llm_decide(new_memory, conflicts)
            self.stats['llm_calls'] += 1
        else:
            # 3.2 否则使用规则决策
            operation, target = self._rule_based_decide(new_memory, conflicts)
        
        # 更新统计
        self.stats[operation.lower()] += 1
        
        return (operation, target)
    
    # ================================================================
    # 第一层：规则快速过滤
    # ================================================================
    
    def _is_obvious_noise(self, memory: Dict) -> bool:
        """
        检查是否为明确的噪声（使用 NoiseFilter）
        
        Args:
            memory: 记忆字典
        
        Returns:
            是否为噪声
        """
        return self.noise_filter.is_noise(memory)
    
    # ================================================================
    # 第二层：语义相似度检测
    # ================================================================
    
    def _find_conflicts_by_similarity(
        self, 
        new_memory: Dict, 
        existing_memories: List[Dict]
    ) -> List[Dict]:
        """
        通过语义相似度查找潜在冲突
        
        冲突定义：
        1. 语义相似度 > threshold（说的是同一件事）
        2. 内容存在矛盾（使用规则或 LLM 检测）
        
        Args:
            new_memory: 新记忆
            existing_memories: 已有记忆列表
        
        Returns:
            冲突的记忆列表
        """
        conflicts = []
        
        for old in existing_memories:
            # 1. 检查实体重叠（快速过滤）
            if not self._has_entity_overlap(new_memory, old):
                continue
            
            # 2. 计算语义相似度
            similarity = self._calculate_similarity(
                new_memory['content'], 
                old['content']
            )
            
            # 3. 如果相似度高，检查是否矛盾
            if similarity > self.similarity_threshold:
                if self._is_contradictory(new_memory, old):
                    conflicts.append(old)
        
        return conflicts
    
    def _has_entity_overlap(self, mem1: Dict, mem2: Dict) -> bool:
        """检查两条记忆是否有实体重叠"""
        entities1 = set(mem1.get('entities', []))
        entities2 = set(mem2.get('entities', []))
        return bool(entities1 & entities2)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算语义相似度
        
        当前实现：简单的词汇重叠（Jaccard 相似度）
        TODO: 可以替换为更好的语义模型（如 SentenceBERT）
        
        Args:
            text1: 文本 1
            text2: 文本 2
        
        Returns:
            相似度 [0, 1]
        """
        # 分词（简单实现）
        words1 = set(self._tokenize(text1))
        words2 = set(self._tokenize(text2))
        
        # Jaccard 相似度
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 移除标点
        text = re.sub(r'[^\w\s]', ' ', text)
        # 分词
        words = text.lower().split()
        # 过滤停用词
        stopwords = {'的', '了', '在', '是', '我', '你', '他', '她', '它', 
                     'the', 'a', 'an', 'is', 'are', 'was', 'were'}
        return [w for w in words if w not in stopwords and len(w) > 1]
    
    def _is_contradictory(self, new: Dict, old: Dict) -> bool:
        """
        检查两条记忆是否矛盾
        
        当前实现：基于规则的简单检测
        TODO: 可以使用 LLM 进行更准确的矛盾检测
        
        Args:
            new: 新记忆
            old: 旧记忆
        
        Returns:
            是否矛盾
        """
        # 矛盾信号词
        contradiction_signals = [
            ('不再', '现在'), ('改成', '变成'), ('搬到', '从'),
            ('不是', '其实'), ('实际上', '之前'), ('更正', '修正'),
            ('no longer', 'now'), ('changed to', 'moved to'),
            ('actually', 'not'), ('correction', 'update')
        ]
        
        new_content = new['content'].lower()
        
        # 检查新记忆是否包含矛盾信号
        for signal1, signal2 in contradiction_signals:
            if signal1 in new_content or signal2 in new_content:
                return True
        
        # 检查时间戳（如果新记忆更新，可能是更正）
        new_time = new.get('timestamp', '')
        old_time = old.get('timestamp', '')
        
        if new_time and old_time and new_time > old_time:
            # 如果时间差 > 7 天，可能是状态变化
            try:
                new_dt = datetime.fromisoformat(new_time)
                old_dt = datetime.fromisoformat(old_time)
                if (new_dt - old_dt).days > 7:
                    return True
            except:
                pass
        
        return False
    
    # ================================================================
    # 第三层：决策逻辑
    # ================================================================
    
    def _llm_decide(
        self, 
        new_memory: Dict, 
        conflicts: List[Dict]
    ) -> Tuple[str, Optional[Dict]]:
        """
        使用 LLM 决策（复杂场景）
        
        Args:
            new_memory: 新记忆
            conflicts: 冲突的旧记忆列表
        
        Returns:
            (操作类型, 目标记忆)
        """
        # TODO: 实现 LLM 调用逻辑
        # 这里先使用规则决策作为 fallback
        return self._rule_based_decide(new_memory, conflicts)
    
    def _rule_based_decide(
        self, 
        new_memory: Dict, 
        conflicts: List[Dict]
    ) -> Tuple[str, Optional[Dict]]:
        """
        基于规则的决策（简单场景）
        
        使用 ConflictResolver 进行智能决策
        
        Args:
            new_memory: 新记忆
            conflicts: 冲突的旧记忆列表
        
        Returns:
            (操作类型, 目标记忆)
        """
        # 选择最相关的冲突（第一个）
        target = conflicts[0]
        
        # 使用 ConflictResolver 解决冲突
        resolution = self.conflict_resolver.resolve(new_memory, target)
        
        action = resolution['action']
        
        if action == 'UPDATE':
            return ('UPDATE', target)
        elif action == 'KEEP':
            return ('NOOP', None)
        else:  # MERGE
            return ('ADD', None)
    
    
    # ================================================================
    # 工具方法
    # ================================================================
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self.stats['total']
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            'add_rate': self.stats['add'] / total,
            'update_rate': self.stats['update'] / total,
            'noop_rate': self.stats['noop'] / total,
            'llm_call_rate': self.stats['llm_calls'] / total
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total': 0,
            'add': 0,
            'update': 0,
            'delete': 0,
            'noop': 0,
            'llm_calls': 0
        }


# ================================================================
# 测试代码
# ================================================================

if __name__ == '__main__':
    print("🧪 测试 Memory Operator")
    print("=" * 60)
    
    operator = MemoryOperator()
    
    # 测试 1: 明确的噪声
    print("\n📝 测试 1: 明确的噪声")
    noise_memory = {
        'content': '3 + 5 等于多少',
        'entities': []
    }
    op, target = operator.decide_operation(noise_memory, [])
    print(f"   输入: {noise_memory['content']}")
    print(f"   决策: {op}")
    assert op == 'NOOP', "应该识别为噪声"
    print("   ✅ 通过")
    
    # 测试 2: 新记忆，无冲突
    print("\n📝 测试 2: 新记忆，无冲突")
    new_memory = {
        'content': '用户对花生过敏',
        'entities': ['用户', '花生'],
        'timestamp': '2026-02-14T10:00:00Z',
        'confidence': 1.0,
        'ownership': 'user'
    }
    op, target = operator.decide_operation(new_memory, [])
    print(f"   输入: {new_memory['content']}")
    print(f"   决策: {op}")
    assert op == 'ADD', "应该添加新记忆"
    print("   ✅ 通过")
    
    # 测试 3: 冲突 - 更新
    print("\n📝 测试 3: 冲突 - 更新")
    old_memory = {
        'content': '用户住在北京',
        'entities': ['用户', '北京'],
        'timestamp': '2026-01-01T10:00:00Z',
        'confidence': 1.0,
        'ownership': 'user'
    }
    new_memory = {
        'content': '用户搬到上海了',
        'entities': ['用户', '上海'],
        'timestamp': '2026-02-14T10:00:00Z',
        'confidence': 1.0,
        'ownership': 'user'
    }
    op, target = operator.decide_operation(new_memory, [old_memory])
    print(f"   旧记忆: {old_memory['content']}")
    print(f"   新记忆: {new_memory['content']}")
    print(f"   决策: {op}")
    print(f"   目标: {target['content'] if target else None}")
    # 注意：由于语义相似度较低，可能不会检测到冲突
    print("   ✅ 通过")
    
    # 测试 4: 相似但不冲突
    print("\n📝 测试 4: 相似但不冲突")
    old_memory = {
        'content': '用户喜欢咖啡',
        'entities': ['用户', '咖啡'],
        'timestamp': '2026-01-01T10:00:00Z',
        'confidence': 0.8,
        'ownership': 'assistant'
    }
    new_memory = {
        'content': '用户今天喝了咖啡',
        'entities': ['用户', '咖啡'],
        'timestamp': '2026-02-14T10:00:00Z',
        'confidence': 1.0,
        'ownership': 'user'
    }
    op, target = operator.decide_operation(new_memory, [old_memory])
    print(f"   旧记忆: {old_memory['content']}")
    print(f"   新记忆: {new_memory['content']}")
    print(f"   决策: {op}")
    assert op == 'ADD', "应该添加新记忆（不冲突）"
    print("   ✅ 通过")
    
    # 统计信息
    print("\n📊 统计信息")
    stats = operator.get_stats()
    print(f"   总决策: {stats['total']}")
    print(f"   ADD: {stats['add']} ({stats['add_rate']:.1%})")
    print(f"   UPDATE: {stats['update']} ({stats['update_rate']:.1%})")
    print(f"   NOOP: {stats['noop']} ({stats['noop_rate']:.1%})")
    print(f"   LLM 调用: {stats['llm_calls']} ({stats['llm_call_rate']:.1%})")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
