#!/usr/bin/env python3
"""
Snapshot Generator - Layer 1 快照自动生成

功能：
- 自动生成工作记忆快照
- 注入到 systemPrompt
- 支持定时更新
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


def load_recent_memories(memory_dir: Path, limit: int = 20) -> List[Dict]:
    """加载最近的记忆"""
    import sqlite3
    # 尝试 memories.db 或 memory.db
    for db_name in ["memories.db", "memory.db"]:
        db_path = memory_dir / "layer2" / db_name
        if db_path.exists():
            break
    else:
        return []
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT content, type, confidence, created, importance
            FROM memories
            ORDER BY confidence DESC, created DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [{"content": r[0], "memory_type": r[1], "confidence": r[2], "created_at": r[3], "importance": r[4]} for r in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def generate_snapshot(memory_dir: Path) -> str:
    """
    生成 Layer 1 快照
    
    Returns:
        markdown 格式的快照
    """
    # 加载最近记忆
    memories = load_recent_memories(memory_dir, limit=20)
    
    # 按类型分组
    facts = [m for m in memories if m.get('memory_type') == 'fact']
    beliefs = [m for m in memories if m.get('memory_type') == 'belief']
    summaries = [m for m in memories if m.get('memory_type') == 'summary']
    
    # 生成快照
    lines = [
        "# 工作记忆快照",
        f"> 生成时间: {datetime.now().isoformat()} | 记忆数: {len(memories)}",
        "",
    ]
    
    # 核心事实 (Top 5)
    if facts:
        lines.append("## 核心事实")
        for i, m in enumerate(facts[:5], 1):
            conf = m.get('confidence', 0)
            content = m.get('content', '')[:50]
            lines.append(f"{i}. [{conf:.2f}] {content}")
        lines.append("")
    
    # 信念/推断
    if beliefs:
        lines.append("## 信念/推断")
        for i, m in enumerate(beliefs[:3], 1):
            conf = m.get('confidence', 0)
            content = m.get('content', '')[:50]
            lines.append(f"{i}. [{conf:.2f}] {content}")
        lines.append("")
    
    # 摘要
    if summaries:
        lines.append("## 摘要")
        for m in summaries[:2]:
            content = m.get('content', '')[:100]
            lines.append(f"- {content}")
        lines.append("")
    
    # 近期要点
    lines.append("## 近期要点")
    lines.append(f"- {datetime.now().strftime('%Y-%m-%d')} 更新")
    lines.append("")
    
    return "\n".join(lines)


def update_snapshot(memory_dir: Path, output_path: Optional[Path] = None):
    """
    更新快照文件
    
    Args:
        memory_dir: 记忆目录
        output_path: 输出路径，默认 memory/layer1/snapshot.md
    """
    if output_path is None:
        output_path = memory_dir / "layer1" / "snapshot.md"
    
    snapshot = generate_snapshot(memory_dir)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(snapshot, encoding='utf-8')
    
    print(f"✅ 快照已更新: {output_path}")


def get_snapshot_for_prompt(memory_dir: Path) -> str:
    """
    获取用于注入 systemPrompt 的快照内容
    
    Returns:
        快照内容（不超过 2000 tokens）
    """
    snapshot_path = memory_dir / "layer1" / "snapshot.md"
    
    if not snapshot_path.exists():
        update_snapshot(memory_dir)
    
    content = snapshot_path.read_text(encoding='utf-8')
    
    # 简单截断（实际应该按 tokens 计数）
    if len(content) > 4000:
        content = content[:4000] + "\n\n... (truncated)"
    
    return content


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="快照生成器")
    parser.add_argument("--dir", default="./memory", help="记忆目录")
    parser.add_argument("--output", help="输出文件")
    args = parser.parse_args()
    
    memory_dir = Path(args.dir)
    output_path = Path(args.output) if args.output else None
    
    update_snapshot(memory_dir, output_path)
