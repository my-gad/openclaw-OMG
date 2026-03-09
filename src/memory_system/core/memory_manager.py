#!/usr/bin/env python3
"""
Memory Manager - 核心记忆管理器

负责记忆的 CRUD 操作、类型管理、置信度控制。
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum


class MemoryType(str, Enum):
    """记忆类型枚举"""
    FACT = "fact"
    BELIEF = "belief"
    SUMMARY = "summary"
    EVENT = "event"


class MemoryRecord:
    """记忆记录类"""
    
    def __init__(
        self,
        content: str,
        memory_type: MemoryType,
        confidence: float = 0.8,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        timestamp: Optional[float] = None,
    ):
        self.id = str(uuid.uuid4())
        self.content = content
        self.memory_type = memory_type
        self.confidence = confidence
        self.tags = tags or []
        self.source = source or "manual"
        self.timestamp = timestamp or datetime.now().timestamp()
        self.last_accessed = self.timestamp
        self.access_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "type": self.memory_type.value,
            "confidence": self.confidence,
            "tags": self.tags,
            "source": self.source,
            "timestamp": self.timestamp,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryRecord":
        """从字典创建"""
        record = cls(
            content=data["content"],
            memory_type=MemoryType(data["type"]),
            confidence=data.get("confidence", 0.8),
            tags=data.get("tags", []),
            source=data.get("source", "manual"),
            timestamp=data.get("timestamp"),
        )
        record.id = data.get("id", record.id)
        record.last_accessed = data.get("last_accessed", record.timestamp)
        record.access_count = data.get("access_count", 0)
        return record
    
    def __repr__(self) -> str:
        return f"MemoryRecord({self.memory_type.value}: {self.content[:50]}...)"


class MemoryManager:
    """
    记忆管理器
    
    负责记忆的添加、删除、更新、检索等核心操作。
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.layer2_active = memory_dir / "layer2" / "active"
        self.layer2_archive = memory_dir / "layer2" / "archive"
        
        # 确保目录存在
        self.layer2_active.mkdir(parents=True, exist_ok=True)
        self.layer2_archive.mkdir(parents=True, exist_ok=True)
        
        # 记忆缓存
        self._cache: Dict[str, MemoryRecord] = {}
        self._load_memories()
    
    def _get_file_path(self, memory_type: MemoryType, archive: bool = False) -> Path:
        """获取记忆文件路径"""
        base = self.layer2_archive if archive else self.layer2_active
        return base / f"{memory_type.value}.jsonl"
    
    def _load_memories(self):
        """加载所有记忆到缓存"""
        for mem_type in MemoryType:
            for archive in [False, True]:
                file_path = self._get_file_path(mem_type, archive)
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                data = json.loads(line)
                                record = MemoryRecord.from_dict(data)
                                self._cache[record.id] = record
    
    def add(self, record: MemoryRecord) -> str:
        """添加记忆"""
        # 保存到文件
        file_path = self._get_file_path(record.memory_type)
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + '\n')
        
        # 更新缓存
        self._cache[record.id] = record
        
        return record.id
    
    def get(self, record_id: str) -> Optional[MemoryRecord]:
        """获取记忆"""
        record = self._cache.get(record_id)
        if record:
            record.last_accessed = datetime.now().timestamp()
            record.access_count += 1
        return record
    
    def delete(self, record_id: str) -> bool:
        """删除记忆"""
        if record_id not in self._cache:
            return False
        
        record = self._cache.pop(record_id)
        
        # 从文件中移除（简化实现：重写文件）
        file_path = self._get_file_path(record.memory_type)
        if file_path.exists():
            records = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data.get('id') != record_id:
                            records.append(line)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(records)
        
        return True
    
    def search(self, query: str, memory_type: Optional[MemoryType] = None, limit: int = 10) -> List[MemoryRecord]:
        """搜索记忆（关键词匹配）"""
        results = []
        query_lower = query.lower()
        
        for record in self._cache.values():
            if memory_type and record.memory_type != memory_type:
                continue
            
            if query_lower in record.content.lower() or \
               any(query_lower in tag.lower() for tag in record.tags):
                results.append(record)
        
        # 按置信度和访问时间排序
        results.sort(key=lambda r: (r.confidence, r.last_accessed), reverse=True)
        
        return results[:limit]
    
    def get_all(self, memory_type: Optional[MemoryType] = None) -> List[MemoryRecord]:
        """获取所有记忆"""
        if memory_type:
            return [r for r in self._cache.values() if r.memory_type == memory_type]
        return list(self._cache.values())
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        stats = {
            "facts": 0,
            "beliefs": 0,
            "summaries": 0,
            "events": 0,
            "total": 0,
        }
        
        for record in self._cache.values():
            key = f"{record.memory_type.value}s"
            if key in stats:
                stats[key] += 1
            stats["total"] += 1
        
        return stats
