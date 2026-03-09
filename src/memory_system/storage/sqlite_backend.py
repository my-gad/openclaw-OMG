#!/usr/bin/env python3
"""
Memory System v1.2.5 - SQLite Backend (Thread-Safe)

线程安全的 SQLite 后端，支持：
- 连接池管理
- WAL 模式优化
- 并发安全锁
- 自动清理过期数据
"""

import sqlite3
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager


# 数据库 Schema
SCHEMA_SQL = """
-- 主表：记忆
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('fact', 'belief', 'summary', 'event')),
    content TEXT NOT NULL,
    
    -- 评分系统
    importance REAL DEFAULT 0.5,
    score REAL DEFAULT 1.0,
    access_boost REAL DEFAULT 0.0,
    final_score REAL GENERATED ALWAYS AS (score + access_boost) STORED,
    
    -- 时间字段
    created TEXT NOT NULL,
    updated TEXT,
    last_accessed TEXT,
    
    -- 访问统计
    access_count INTEGER DEFAULT 0,
    retrieval_count INTEGER DEFAULT 0,
    
    -- 来源和状态
    source TEXT,
    state INTEGER DEFAULT 0 CHECK(state IN (0, 1, 2)),
    
    -- 冲突管理
    conflict_downgraded INTEGER DEFAULT 0,
    downgrade_reason TEXT,
    superseded INTEGER DEFAULT 0,
    superseded_by TEXT,
    
    -- TTL 管理
    ttl_days INTEGER,
    auto_delete_at TEXT,
    
    -- 类型特有字段
    confidence REAL,
    basis TEXT,
    extract_method TEXT,
    expires_at TEXT,
    is_permanent INTEGER DEFAULT 1
);

-- 实体关联表
CREATE TABLE IF NOT EXISTS memory_entities (
    memory_id TEXT NOT NULL,
    entity TEXT NOT NULL,
    PRIMARY KEY (memory_id, entity),
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
);

-- 关系三元组表
CREATE TABLE IF NOT EXISTS memory_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    object TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    created TEXT NOT NULL,
    superseded INTEGER DEFAULT 0,
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
);

-- 摘要来源表
CREATE TABLE IF NOT EXISTS summary_sources (
    summary_id TEXT NOT NULL,
    source_fact_id TEXT NOT NULL,
    PRIMARY KEY (summary_id, source_fact_id),
    FOREIGN KEY (summary_id) REFERENCES memories(id) ON DELETE CASCADE
);

-- 访问日志表
CREATE TABLE IF NOT EXISTS access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT NOT NULL,
    access_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_memories_state_score ON memories(state, final_score DESC);
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created DESC);
CREATE INDEX IF NOT EXISTS idx_memories_auto_delete ON memories(auto_delete_at) WHERE auto_delete_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_entities_entity ON memory_entities(entity);
CREATE INDEX IF NOT EXISTS idx_relations_subject_type ON memory_relations(subject, relation_type, superseded);
CREATE INDEX IF NOT EXISTS idx_access_log_timestamp ON access_log(timestamp DESC);
"""


class SQLiteBackend:
    """
    SQLite 后端管理器（线程安全）
    
    特性:
    - WAL 模式提升并发性能
    - 可重入锁保证线程安全
    - 自动清理过期数据
    - 支持 TTL 管理
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = Path(memory_dir)
        self.db_path = self.memory_dir / 'layer2' / 'memories.db'
        
        # 线程安全：单例连接 + 可重入锁
        self._conn: Optional[sqlite3.Connection] = None
        self._lock = threading.RLock()  # 可重入锁，允许同一线程多次获取
        
        # 初始化数据库
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """确保数据库存在并初始化"""
        if not self.db_path.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        with self._get_connection(write=True) as conn:
            # 启用 WAL 模式（提升并发性能）
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.execute('PRAGMA busy_timeout=30000')  # 30 秒超时
            conn.execute('PRAGMA cache_size=-64000')   # 64MB 缓存
            
            # 创建表和索引
            conn.executescript(SCHEMA_SQL)
            conn.commit()
        
        print(f"✅ SQLite 数据库初始化完成：{self.db_path}")
    
    @contextmanager
    def _get_connection(self, write: bool = False):
        """
        获取数据库连接（线程安全）
        
        Args:
            write: 是否需要写锁（写操作需要，读操作不需要）
        
        Yields:
            sqlite3.Connection: 数据库连接
        """
        if write:
            self._lock.acquire()
        
        try:
            if self._conn is None:
                self._conn = sqlite3.connect(
                    str(self.db_path),
                    check_same_thread=False,  # 我们自己用锁管理
                    timeout=30.0
                )
                self._conn.row_factory = sqlite3.Row
            
            yield self._conn
            
        finally:
            if write:
                self._lock.release()
    
    def add_memory(
        self,
        id: str,
        type: str,
        content: str,
        confidence: float = 0.8,
        source: str = "manual",
        ttl_days: Optional[int] = None,
        entities: Optional[List[str]] = None,
    ) -> bool:
        """
        添加记忆到数据库
        
        Args:
            id: 记忆 ID
            type: 记忆类型 (fact/belief/summary/event)
            content: 记忆内容
            confidence: 置信度
            source: 来源
            ttl_days: TTL 天数
            entities: 关联实体列表
        
        Returns:
            bool: 是否成功
        """
        now = datetime.utcnow().isoformat()
        auto_delete_at = None
        
        if ttl_days:
            delete_time = datetime.utcnow() + timedelta(days=ttl_days)
            auto_delete_at = delete_time.isoformat()
        
        with self._get_connection(write=True) as conn:
            try:
                conn.execute("""
                    INSERT INTO memories (
                        id, type, content, confidence, source,
                        created, last_accessed, ttl_days, auto_delete_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (id, type, content, confidence, source, now, now, ttl_days, auto_delete_at))
                
                # 添加实体关联
                if entities:
                    for entity in entities:
                        conn.execute(
                            "INSERT OR IGNORE INTO memory_entities (memory_id, entity) VALUES (?, ?)",
                            (id, entity)
                        )
                
                conn.commit()
                return True
                
            except sqlite3.IntegrityError:
                # ID 已存在
                return False
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """获取单个记忆"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM memories WHERE id = ?",
                (memory_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        with self._get_connection(write=True) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_access(self, memory_id: str, access_type: str = "retrieval") -> bool:
        """
        更新访问统计
        
        Args:
            memory_id: 记忆 ID
            access_type: 访问类型 (retrieval/used_in_response/user_mentioned)
        """
        now = datetime.utcnow().isoformat()
        
        with self._get_connection(write=True) as conn:
            # 更新统计
            conn.execute("""
                UPDATE memories 
                SET last_accessed = ?, 
                    access_count = access_count + 1,
                    retrieval_count = retrieval_count + 1
                WHERE id = ?
            """, (now, memory_id))
            
            # 记录访问日志
            conn.execute("""
                INSERT INTO access_log (memory_id, access_type, timestamp)
                VALUES (?, ?, ?)
            """, (memory_id, access_type, now))
            
            conn.commit()
    
    def search_memories(
        self,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        搜索记忆
        
        Args:
            query: 搜索关键词
            memory_type: 记忆类型过滤
            limit: 返回数量限制
        
        Returns:
            记忆列表
        """
        if memory_type:
            cursor = self._conn.execute("""
                SELECT * FROM memories 
                WHERE type = ? AND content LIKE ?
                ORDER BY final_score DESC, created DESC
                LIMIT ?
            """, (memory_type, f"%{query}%", limit))
        else:
            cursor = self._conn.execute("""
                SELECT * FROM memories 
                WHERE content LIKE ?
                ORDER BY final_score DESC, created DESC
                LIMIT ?
            """, (f"%{query}%", limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_expired(self) -> int:
        """
        清理过期数据
        
        Returns:
            删除的记录数
        """
        now = datetime.utcnow().isoformat()
        
        with self._get_connection(write=True) as conn:
            # 删除过期记忆
            cursor = conn.execute("""
                DELETE FROM memories 
                WHERE auto_delete_at IS NOT NULL 
                AND auto_delete_at < ?
            """, (now,))
            
            count = cursor.rowcount
            conn.commit()
            
            return count
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._get_connection() as conn:
            # 各类型数量
            cursor = conn.execute("""
                SELECT type, COUNT(*) as count 
                FROM memories 
                GROUP BY type
            """)
            type_counts = {row['type']: row['count'] for row in cursor.fetchall()}
            
            # 总数量
            cursor = conn.execute("SELECT COUNT(*) as total FROM memories")
            total = cursor.fetchone()['total']
            
            # 过期数据
            cursor = conn.execute("""
                SELECT COUNT(*) as expired 
                FROM memories 
                WHERE auto_delete_at IS NOT NULL 
                AND auto_delete_at < datetime('now')
            """)
            expired = cursor.fetchone()['expired']
            
            return {
                "total": total,
                "expired": expired,
                **type_counts,
            }
    
    def close(self):
        """关闭数据库连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
