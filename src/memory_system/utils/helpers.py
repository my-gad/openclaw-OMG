#!/usr/bin/env python3
"""
Helper functions - 辅助工具函数
"""

import re
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本到指定长度"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """清理文本：去除多余空白、标准化格式"""
    # 去除首尾空白
    text = text.strip()
    # 标准化空白字符
    text = re.sub(r'\s+', ' ', text)
    # 去除控制字符
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    return text


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """提取关键词 (简化版)"""
    # 中文按字符频率，英文按单词
    words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
    
    # 简单词频统计
    word_freq = {}
    for word in words:
        if len(word) > 1:  # 跳过单字符
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # 排序取前 N 个
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]


def generate_id(content: str, prefix: str = "") -> str:
    """生成唯一 ID"""
    hash_str = hashlib.md5(content.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_str}" if prefix else hash_str


def format_timestamp(timestamp: Optional[float] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化时间戳"""
    dt = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
    return dt.strftime(format_str)


def parse_time_ago(text: str) -> Optional[datetime]:
    """解析相对时间 (如 '3 天前', '2 小时前')"""
    match = re.search(r'(\d+)([天时分钟])前', text)
    if not match:
        return None
    
    value = int(match.group(1))
    unit = match.group(2)
    
    now = datetime.now()
    
    if unit == '天':
        from datetime import timedelta
        return now - timedelta(days=value)
    elif unit == '小时':
        from datetime import timedelta
        return now - timedelta(hours=value)
    elif unit == '分钟':
        from datetime import timedelta
        return now - timedelta(minutes=value)
    elif unit == '年':
        return now.replace(year=now.year - value)
    
    return None


def is_chinese(text: str) -> bool:
    """判断是否主要为中文"""
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    return chinese_chars / len(text) > 0.5 if text else False


def split_sentences(text: str) -> List[str]:
    """分割句子"""
    # 中英文句子分割
    sentences = re.split(r'[.!?。！？\n]+', text)
    return [s.strip() for s in sentences if s.strip()]


def merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """合并重叠区间"""
    if not intervals:
        return []
    
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_intervals[0]]
    
    for current in sorted_intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
    
    return merged


def calculate_overlap_ratio(text1: str, text2: str) -> float:
    """计算两段文本的重叠度"""
    set1 = set(text1.lower())
    set2 = set(text2.lower())
    
    if not set1 or not set2:
        return 0.0
    
    intersection = set1 & set2
    union = set1 | set2
    
    return len(intersection) / len(union) if union else 0.0


def safe_json_load(content: str, default: Any = None):
    """安全地解析 JSON"""
    import json
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dump(obj: Any, indent: int = 2) -> str:
    """安全地序列化 JSON"""
    import json
    try:
        return json.dumps(obj, ensure_ascii=False, indent=indent)
    except (TypeError, ValueError):
        return "{}"
