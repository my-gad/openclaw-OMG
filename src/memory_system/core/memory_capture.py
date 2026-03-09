#!/usr/bin/env python3
"""
Memory Capture - 即时记忆捕获模块

功能：
- 即时捕获用户消息
- 重要性评分
- 待处理队列管理
- 关键词触发检测
"""

import os
import re
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict


# 触发关键词
TRIGGER_KEYWORDS = {
    # Layer 0 - 显式时间相关
    "layer0_explicit": ["之前", "上次", "以前", "曾经", "以前", "那天", "那次的"],
    "layer0_time": ["昨天", "上周", "去年", "小时候", "以前"],
    
    # Layer 1 - 身份/偏好/关系
    "layer1_preference": ["我喜欢", "我讨厌", "我想要", "我不想要", "偏好", "喜欢", "讨厌"],
    "layer1_identity": ["我是", "我叫", "我的名字", "职业", "工作"],
    "layer1_relation": ["我老婆", "我老公", "我家人", "我朋友", "我爸", "我妈", "我"],
    "layer1_project": ["项目", "任务", "在做", "开发", "做的"],
    
    # 显式记忆请求
    "explicit_recall": ["你记得", "还记得", "帮我回忆", "以前说过", "之前说过"],
}


# 重要性评分关键词
IMPORTANCE_KEYWORDS = {
    "high": ["过敏", "疾病", "重要", "必须", "绝对", "永远", "记住", "不要忘记"],
    "medium": ["喜欢", "讨厌", "习惯", "经常", "通常", "一般"],
    "low": ["可能", "也许", "大概", "应该", "或许"],
}


@dataclass
class MemoryRecord:
    """记忆记录"""
    id: str
    content: str
    source: str  # "user", "assistant", "system"
    created: str  # ISO 时间
    urgent: bool
    importance: float  # 0-1
    category: str  # "fact", "belief", "preference", "identity", "relation"
    session_id: Optional[str] = None
    message_index: Optional[int] = None


def check_urgency(content: str) -> Tuple[bool, float, str]:
    """
    检查内容紧急程度和重要性
    
    Returns:
        (is_urgent, importance, category)
    """
    content_lower = content.lower()
    
    # 检测类别
    category = "fact"
    for kw in IMPORTANCE_KEYWORDS["high"]:
        if kw in content:
            category = "fact"
            break
    
    for kw in TRIGGER_KEYWORDS["layer1_preference"]:
        if kw in content:
            category = "preference"
            break
    
    for kw in TRIGGER_KEYWORDS["layer1_identity"]:
        if kw in content:
            category = "identity"
            break
    
    for kw in TRIGGER_KEYWORDS["layer1_relation"]:
        if kw in content:
            category = "relation"
            break
    
    # 计算重要性
    importance = 0.5  # 默认
    
    for kw in IMPORTANCE_KEYWORDS["high"]:
        if kw in content:
            importance = 0.9
            break
    
    for kw in IMPORTANCE_KEYWORDS["medium"]:
        if kw in content:
            importance = 0.7
            break
    
    for kw in IMPORTANCE_KEYWORDS["low"]:
        if kw in content:
            importance = 0.3
            break
    
    # 紧急判断
    is_urgent = importance >= 0.8
    
    return is_urgent, importance, category


def detect_trigger_layer(query: str) -> Tuple[int, str, List[str]]:
    """
    检测查询触发的记忆层
    
    Returns:
        (layer, trigger_type, matched_keywords)
    """
    query_lower = query.lower()
    matched_keywords = []
    
    # Layer 0 - 显式时间
    for trigger_type in ["layer0_explicit", "layer0_time"]:
        keywords = TRIGGER_KEYWORDS.get(trigger_type, [])
        for kw in keywords:
            if kw in query:
                matched_keywords.append(kw)
        if matched_keywords:
            return 0, trigger_type, matched_keywords
    
    # Layer 1 - 身份/偏好
    for trigger_type in ["layer1_preference", "layer1_identity", "layer1_relation", "layer1_project"]:
        keywords = TRIGGER_KEYWORDS.get(trigger_type, [])
        for kw in keywords:
            if kw in query:
                matched_keywords.append(kw)
        if matched_keywords:
            return 1, trigger_type, matched_keywords
    
    # 显式记忆请求
    for kw in TRIGGER_KEYWORDS.get("explicit_recall", []):
        if kw in query:
            matched_keywords.append(kw)
    if matched_keywords:
        return 1, "explicit_recall", matched_keywords
    
    # 默认不触发
    return -1, "none", []


def now_iso() -> str:
    """获取当前 ISO 时间"""
    return datetime.now().isoformat()


def load_pending(memory_dir: Path) -> List[Dict]:
    """加载待处理队列"""
    pending_path = memory_dir / "layer2" / "pending.jsonl"
    if not pending_path.exists():
        return []
    
    records = []
    with open(pending_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def save_pending(memory_dir: Path, records: List[Dict]):
    """保存待处理队列"""
    pending_path = memory_dir / "layer2" / "pending.jsonl"
    pending_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(pending_path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def capture_memory(
    memory_dir: Path,
    content: str,
    source: str = "user",
    session_id: Optional[str] = None,
    message_index: Optional[int] = None,
) -> Dict[str, Any]:
    """
    即时捕获记忆
    
    Args:
        memory_dir: 记忆目录
        content: 记忆内容
        source: 来源 (user/assistant/system)
        session_id: 会话 ID
        message_index: 消息索引
    
    Returns:
        捕获的记录
    """
    is_urgent, importance, category = check_urgency(content)
    
    record = {
        "id": f"p_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}",
        "content": content,
        "source": source,
        "created": now_iso(),
        "urgent": is_urgent,
        "importance": importance,
        "category": category,
        "session_id": session_id,
        "message_index": message_index,
    }
    
    # 添加到待处理队列
    pending = load_pending(memory_dir)
    pending.append(record)
    save_pending(memory_dir, pending)
    
    return record


def search_pending(memory_dir: Path, query: str) -> List[Dict]:
    """
    搜索待处理队列
    
    Args:
        memory_dir: 记忆目录
        query: 查询关键词
    
    Returns:
        匹配的记录列表
    """
    pending = load_pending(memory_dir)
    if not pending:
        return []
    
    results = []
    query_words = set(re.findall(r"[\u4e00-\u9fa5]+|[a-zA-Z]+", query.lower()))
    
    for record in pending:
        content_lower = record.get("content", "").lower()
        content_words = set(re.findall(r"[\u4e00-\u9fa5]+|[a-zA-Z]+", content_lower))
        
        # 简单匹配
        if query_words & content_words:
            results.append(record)
    
    return results


def get_pending_count(memory_dir: Path) -> int:
    """获取待处理队列数量"""
    return len(load_pending(memory_dir))


def clear_pending(memory_dir: Path):
    """清空待处理队列"""
    save_pending(memory_dir, [])
