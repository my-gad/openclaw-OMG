#!/usr/bin/env python3
"""
Entity System - 实体识别与隔离系统

核心功能:
1. 三层实体识别 (硬编码 → 学习 → LLM)
2. 动态实体学习与模式归纳
3. 竞争性抑制 (实体隔离)
4. 学习实体清理
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 默认配置
ENTITY_SYSTEM_CONFIG = {
    # 内置实体模式 (硬编码)
    "builtin_patterns": [
        r"机器人[_\-]?\d+",
        r"项目[_\-]?[A-Z]",
        r"城市[_\-]?\d+",
        r"用户[_\-]?\d+",
        r"Agent[_\-]?\d+",
        r"协议[_\-]?[A-Z]",
    ],
    # 学习配置
    "learning": {
        "min_similar_for_pattern": 3,  # 至少 3 个相似实体才归纳模式
        "max_learned_entities": 1000,  # 最大学习实体数
        "max_learned_patterns": 100,   # 最大学习模式数
        "ttl_days": 365,               # 未使用实体的保留天数
    },
    # 隔离配置
    "isolation": {
        "inhibition_factor": 0.1,      # 抑制系数 (断崖降权)
        "similarity_threshold": 0.5,   # 相似度阈值
        "min_common_prefix_ratio": 0.5, # 最小共同前缀比例
    },
}

# 引号实体模式 (支持中英文引号)
QUOTED_ENTITY_PATTERNS = [
    r"\u300c([^\u300d]+)\u300d",  # 中文单引号「」
    r"\u300e([^\u300f]+)\u300f",  # 中文双引号『』
    r"\u201c([^\u201d]+)\u201d",  # 中文弯引号""
    r"\u2018([^\u2019]+)\u2019",  # 中文弯引号''
    r"\u300a([^\u300b]+)\u300b",  # 书名号《》
    r"'([^']+)'",                 # 英文单引号
    r'"([^"]+)"',                 # 英文双引号
]


class EntitySystem:
    """
    实体识别与管理系统
    
    支持：
    - 内置模式识别
    - 学习实体识别
    - 引号实体提取
    - 实体隔离与抑制
    """
    
    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = memory_dir
        self.config = ENTITY_SYSTEM_CONFIG.copy()
        
        # 学习实体
        self.learned_entities: List[str] = []
        self.learned_patterns: List[str] = []
        self.access_stats: Dict[str, Any] = {}
        
        # 加载学习数据
        if memory_dir:
            self._load_learned_entities()
    
    def _get_learned_path(self) -> Path:
        """获取学习实体文件路径"""
        path = self.memory_dir / "layer2" / "learned_entities.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    
    def _load_learned_entities(self):
        """加载学习实体"""
        path = self._get_learned_path()
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learned_entities = data.get("exact", [])
                    self.learned_patterns = data.get("patterns", [])
                    self.access_stats = data.get("access_stats", {})
            except (json.JSONDecodeError, IOError):
                pass
    
    def save_learned_entities(self):
        """保存学习实体"""
        if not self.memory_dir:
            return
        
        path = self._get_learned_path()
        data = {
            "exact": self.learned_entities,
            "patterns": self.learned_patterns,
            "access_stats": self.access_stats,
            "last_updated": datetime.utcnow().isoformat() + 'Z',
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """
        提取内容中的实体
        
        返回：[(entity, type, confidence, source), ...]
        """
        entities = []
        
        # 1. 提取引号实体 (最高优先级)
        entities.extend(self._extract_quoted_entities(content))
        
        # 2. 内置模式识别
        entities.extend(self._extract_builtin_entities(content))
        
        # 3. 学习实体识别
        entities.extend(self._extract_learned_entities(content))
        
        return entities
    
    def _extract_quoted_entities(self, content: str) -> List[Dict[str, Any]]:
        """提取引号中的实体"""
        entities = []
        
        for pattern in QUOTED_ENTITY_PATTERNS:
            matches = re.findall(pattern, content)
            for match in matches:
                entities.append({
                    "entity": match.strip(),
                    "type": "quoted",
                    "confidence": 0.95,
                    "source": "quote",
                })
        
        return entities
    
    def _extract_builtin_entities(self, content: str) -> List[Dict[str, Any]]:
        """提取内置模式实体"""
        entities = []
        
        for pattern in self.config["builtin_patterns"]:
            matches = re.findall(pattern, content)
            for match in matches:
                entities.append({
                    "entity": match,
                    "type": "builtin",
                    "confidence": 0.85,
                    "source": "builtin",
                })
        
        return entities
    
    def _extract_learned_entities(self, content: str) -> List[Dict[str, Any]]:
        """提取学习实体"""
        entities = []
        
        # 精确匹配
        for entity in self.learned_entities:
            if entity in content:
                entities.append({
                    "entity": entity,
                    "type": "learned",
                    "confidence": 0.75,
                    "source": "learned",
                })
        
        # 模式匹配
        for pattern in self.learned_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                entities.append({
                    "entity": match,
                    "type": "learned_pattern",
                    "confidence": 0.70,
                    "source": "learned_pattern",
                })
        
        return entities
    
    def learn_entity(self, entity: str, entity_type: str = "custom"):
        """
        学习新实体
        
        Args:
            entity: 实体内容
            entity_type: 实体类型
        """
        if entity not in self.learned_entities:
            self.learned_entities.append(entity)
            
            # 限制数量
            max_entities = self.config["learning"]["max_learned_entities"]
            if len(self.learned_entities) > max_entities:
                self.learned_entities = self.learned_entities[-max_entities:]
    
    def learn_pattern(self, pattern: str):
        """
        学习新模式
        
        Args:
            pattern: 正则表达式模式
        """
        if pattern not in self.learned_patterns:
            self.learned_patterns.append(pattern)
            
            # 限制数量
            max_patterns = self.config["learning"]["max_learned_patterns"]
            if len(self.learned_patterns) > max_patterns:
                self.learned_patterns = self.learned_patterns[-max_patterns:]
    
    def apply_isolation(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        应用竞争性抑制 (断崖降权)
        
        对于相似但不同的实体，降低其权重
        """
        if not entities:
            return entities
        
        inhibition_factor = self.config["isolation"]["inhibition_factor"]
        threshold = self.config["isolation"]["similarity_threshold"]
        
        # 按置信度排序
        sorted_entities = sorted(entities, key=lambda x: x["confidence"], reverse=True)
        
        result = []
        for entity in sorted_entities:
            # 检查是否与高置信度实体相似
            is_suppressed = False
            
            for high_entity in result:
                if high_entity["confidence"] >= threshold:
                    similarity = self._calculate_similarity(
                        entity["entity"], 
                        high_entity["entity"]
                    )
                    
                    if similarity > 0 and similarity < 1.0:
                        # 相似但不完全相同，应用抑制
                        entity["confidence"] *= inhibition_factor
                        is_suppressed = True
                        break
            
            result.append(entity)
        
        return result
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """计算两个字符串的相似度 (简单前缀匹配)"""
        if not s1 or not s2:
            return 0.0
        
        # 计算共同前缀
        min_len = min(len(s1), len(s2))
        common_prefix_len = 0
        
        for i in range(min_len):
            if s1[i] == s2[i]:
                common_prefix_len += 1
            else:
                break
        
        ratio = common_prefix_len / max(len(s1), len(s2))
        return ratio if ratio > self.config["isolation"]["min_common_prefix_ratio"] else 0.0
    
    def cleanup_old_entities(self, days_threshold: int = 365):
        """清理长时间未使用的实体"""
        if not self.access_stats:
            return
        
        cutoff = datetime.utcnow().timestamp() - (days_threshold * 24 * 3600)
        
        # 清理未访问的实体
        new_entities = []
        for entity in self.learned_entities:
            stats = self.access_stats.get(entity, {})
            last_access = stats.get("last_access", 0)
            
            if last_access > cutoff or not stats:
                new_entities.append(entity)
        
        self.learned_entities = new_entities
        self.save_learned_entities()
