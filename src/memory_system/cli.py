#!/usr/bin/env python3
"""
Memory System CLI - 三层记忆架构命令行接口

使用方法:
    python -m memory_system.cli init          # 初始化
    python -m memory_system.cli add "内容"    # 添加记忆
    python -m memory_system.cli search "词"   # 搜索
    python -m memory_system.cli consolidate   # 整合
    python -m memory_system.cli status        # 状态
    python -m memory_system.cli export        # 导出
    python -m memory_system.cli import        # 导入
    python -m memory_system.cli cleanup       # 清理
"""

import argparse
import sys
import json
import csv
from pathlib import Path
from typing import Optional
from datetime import datetime

from memory_system import __version__
from memory_system.core.memory_manager import MemoryManager, MemoryRecord, MemoryType
from memory_system.core.consolidation import ConsolidationEngine, ConsolidationConfig
from memory_system.utils.config import Config

# 多 Agent 支持
try:
    from memory_system.multiagent.agent_manager import AgentManager, AgentRole, AgentStatus
    from memory_system.multiagent.organization import OrganizationManager, OrgType
    from memory_system.multiagent.auto_register import get_or_create_agent
    MULTIAGENT_ENABLED = True
except ImportError:
    MULTIAGENT_ENABLED = False


def ensure_current_agent(memory_dir: Path) -> Optional[str]:
    """
    确保当前 Agent 已注册
    
    Returns:
        Agent ID，如果失败返回 None
    """
    if not MULTIAGENT_ENABLED:
        return None
    
    try:
        # 自动注册当前 Agent
        agent_id, is_new = get_or_create_agent(memory_dir=memory_dir)
        if is_new:
            print(f"✅ 自动注册 Agent: {agent_id[:8]}...")
        return agent_id
    except Exception as e:
        print(f"⚠️ 自动注册失败: {e}")
        return None


def get_memory_manager(args) -> Optional[MemoryManager]:
    """获取记忆管理器实例"""
    # 默认使用 OpenClaw 记忆目录
    default_memory_dir = Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    memory_dir = Path(args.dir) if hasattr(args, 'dir') and args.dir else default_memory_dir
    if not memory_dir.exists():
        return None
    return MemoryManager(memory_dir)


def init_command(args):
    """初始化记忆系统"""
    print(f"🧠 初始化 Memory System v{__version__}")
    
    # 默认使用 OpenClaw 记忆目录
    default_memory_dir = Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    memory_dir = Path(args.dir) if args.dir else default_memory_dir
    
    # 创建目录结构
    dirs = [
        memory_dir / "layer1",
        memory_dir / "layer2" / "active",
        memory_dir / "layer2" / "archive",
        memory_dir / "layer2" / "entities",
        memory_dir / "layer3",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f" ✓ 创建目录：{d}")
    
    # 创建配置文件
    config = Config(str(memory_dir / "config.json"))
    config.set("memory_dir", str(memory_dir))
    config.save()
    print(f" ✓ 创建配置文件：{memory_dir / 'config.json'}")
    
    # 创建初始快照
    snapshot_path = memory_dir / "layer1" / "snapshot.md"
    snapshot_path.write_text(
        "# 工作记忆快照\n\n系统已初始化，等待首次对话...\n",
        encoding='utf-8'
    )
    print(f" ✓ 创建快照文件：{snapshot_path}")

    # 自动安装 Cron 定时任务
    print("\n⏰ 安装 Cron 定时任务...")
    try:
        from memory_system.integration.openclaw_integration import install_cron
        if install_cron():
            print(" ✓ Cron 定时任务已安装")
            print("   - 每天 03:00 执行记忆整合")
            print("   - 每小时更新快照")
        else:
            print(" ℹ️ Cron 任务已存在，无需重复安装")
    except Exception as e:
        print(f" ⚠️ Cron 安装失败: {e}")

    
    print(f"\n✅ 初始化完成！记忆目录：{memory_dir.absolute()}")


def add_command(args):
    """添加记忆"""
    content = args.content
    memory_type_str = args.type
    confidence = args.confidence
    
    print(f"📝 添加记忆：{content[:50]}...")
    
    memory_dir = Path(args.dir) if args.dir else Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化，先运行 'memory-system init'")
        return
    
    # 确保当前 Agent 已注册
    ensure_current_agent(memory_dir)
    
    manager = MemoryManager(memory_dir)
    
    try:
        memory_type = MemoryType(memory_type_str)
    except ValueError:
        print(f"❌ 无效的记忆类型：{memory_type_str}")
        return
    
    record = MemoryRecord(
        content=content,
        memory_type=memory_type,
        confidence=confidence,
        tags=args.tags.split(',') if args.tags else [],
        source="cli",
    )
    
    record_id = manager.add(record)
    print(f"✅ 记忆已添加，ID: {record_id}")


def capture_command(args):
    """即时捕获记忆（自动评分）"""
    content = args.content
    source = args.source or "user"
    session_id = args.session
    message_index = args.index
    
    print(f"📸 捕获记忆：{content[:50]}...")
    
    memory_dir = Path(args.dir) if args.dir else Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化，先运行 'memory-system init'")
        return
    
    # 确保当前 Agent 已注册
    ensure_current_agent(memory_dir)
    
    # 导入捕获模块
    from memory_system.core.memory_capture import capture_memory, detect_trigger_layer
    
    # 检测触发层
    layer, trigger_type, keywords = detect_trigger_layer(content)
    
    # 捕获记忆
    record = capture_memory(
        memory_dir=memory_dir,
        content=content,
        source=source,
        session_id=session_id,
        message_index=message_index,
    )
    
    print(f"✅ 记忆已捕获")
    print(f"   重要性: {record['importance']:.1f}")
    print(f"   类别: {record['category']}")
    print(f"   触发层: {layer}")
    if record.get('session_id'):
        print(f"   来源: {record['session_id']}:{record.get('message_index', '?')}")


def search_command(args):
    """搜索记忆"""
    query = args.query
    print(f"🔍 搜索：{query}")
    
    memory_dir = Path(args.dir) if args.dir else Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = MemoryManager(memory_dir)
    results = manager.search(query, limit=args.top_k)
    
    if not results:
        print("未找到匹配的记忆")
        return
    
    print(f"\n找到 {len(results)} 条相关记忆:\n")
    for i, record in enumerate(results, 1):
        print(f"{i}. [{record.memory_type.value}] {record.content[:80]}")
        print(f"   置信度：{record.confidence:.2f}, 访问次数：{record.access_count}")
        print()


def consolidate_command(args):
    """执行记忆整合"""
    print("🔄 执行记忆整合...")
    
    memory_dir = Path(args.dir) if args.dir else Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = MemoryManager(memory_dir)
    events = manager.get_all(MemoryType.EVENT)
    
    if not events:
        print("没有待处理的事件，尝试整合所有记忆...")
        events = manager.get_all()
    
    if not events:
        print("❌ 没有任何记忆可整合")
        return
    
    config = ConsolidationConfig()
    engine = ConsolidationEngine(manager, config)
    
    event_dicts = [e.to_dict() for e in events]
    report = engine.run(event_dicts)
    
    print("\n=== 整合报告 ===")
    print(f"开始时间：{report['start_time']}")
    print(f"结束时间：{report['end_time']}")
    print(f"处理数量：{report['summary']['processed']}")
    print(f"保留数量：{report['summary']['kept']}")
    print(f"归档数量：{report['summary']['archived']}")
    print(f"删除数量：{report['summary']['deleted']}")


def status_command(args):
    """查看系统状态"""
    print(f"📊 Memory System v{__version__} 状态\n")
    
    memory_dir = Path(args.dir) if args.dir else Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化，运行 'memory-system init'")
        return
    
    stats = {"facts": 0, "beliefs": 0, "summaries": 0, "entities": 0}
    
    layer2 = memory_dir / "layer2" / "active"
    if layer2.exists():
        for mem_type in ["fact", "belief", "summary", "event"]:
            file_path = layer2 / f"{mem_type}.jsonl"
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        stats[f"{mem_type}s"] = sum(1 for line in f if line.strip())
                except:
                    pass
    
    # 待处理队列
    from memory_system.core.memory_capture import get_pending_count
    pending_count = get_pending_count(memory_dir)
    
    print("存储统计:")
    print(f" - Facts:     {stats['facts']:>6} 条")
    print(f" - Beliefs:   {stats['beliefs']:>6} 条")
    print(f" - Summaries: {stats['summaries']:>6} 条")
    print(f" - Events:    {stats.get('events', 0):>6} 条")
    print(f" - 待处理:    {pending_count:>6} 条")
    
    db_path = memory_dir / "layer2" / "memories.db"
    if db_path.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memories")
            count = cursor.fetchone()[0]
            print(f"\nSQLite 数据库：{count} 条记录")
            conn.close()
        except:
            pass
    
    print(f"\n记忆目录：{memory_dir.absolute()}")


def export_command(args):
    """导出记忆"""
    memory_dir = Path(args.dir) if args.dir else Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = MemoryManager(memory_dir)
    records = manager.get_all()
    
    if not records:
        print("❌ 没有记忆可导出")
        return
    
    output_file = args.output or memory_dir / "export.json"
    format = args.format or "json"
    
    if format == "json":
        data = [r.to_dict() for r in records]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    elif format == "csv":
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'type', 'content', 'confidence', 'timestamp'])
            for r in records:
                writer.writerow([r.id, r.memory_type.value, r.content, r.confidence, r.timestamp])
    
    print(f"✅ 已导出 {len(records)} 条记录到 {output_file}")


def import_command(args):
    """导入记忆"""
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"❌ 文件不存在：{input_file}")
        return
    
    memory_dir = Path(args.dir) if args.dir else Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = MemoryManager(memory_dir)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            if input_file.suffix == '.json':
                data = json.load(f)
            else:
                print("❌ 仅支持 JSON 格式导入")
                return
    except Exception as e:
        print(f"❌ 导入失败：{e}")
        return
    
    count = 0
    for item in data:
        try:
            record = MemoryRecord.from_dict(item)
            manager.add(record)
            count += 1
        except Exception as e:
            print(f"⚠️ 跳过无效记录：{e}")
    
    print(f"✅ 已导入 {count}/{len(data)} 条记录")


def integration_command(args):
    """OpenClaw 集成命令"""
    from memory_system.integration.openclaw_integration import (
        inject_to_system_prompt,
        capture_from_message,
        run_consolidation,
        generate_cron_config,
        install_cron,
        get_integration_status,
    )
    
    if args.inject:
        success = inject_to_system_prompt(args.inject)
        if success:
            print(f"✅ 快照已注入到 Agent {args.inject}")
        else:
            print(f"❌ 注入失败")
    
    elif args.capture:
        msg, session, idx = args.capture
        result = capture_from_message(msg, session, int(idx))
        if result.get("success"):
            print(f"✅ 消息已捕获")
        else:
            print(f"❌ 捕获失败: {result.get('error')}")
    
    elif args.consolidate:
        result = run_consolidation()
        if result.get("success"):
            print(f"✅ 记忆整合完成")
        else:
            print(f"❌ 整合失败: {result.get('error')}")
    
    elif args.cron:
        print(generate_cron_config())
    
    elif args.install_cron:
        if install_cron():
            print(f"✅ Cron 定时任务已安装")
        else:
            print(f"ℹ️ Cron 任务已存在，无需重复安装")
    
    elif args.status:
        status = get_integration_status()
        print("📊 集成状态:")
        print(f" - OpenClaw 配置: {'✅' if status['openclaw_config_exists'] else '❌'}")
        print(f" - 记忆目录: {'✅' if status['memory_dir_exists'] else '❌'}")
        print(f" - 快照可用: {'✅' if status['snapshot_available'] else '❌'}")
        print(f" - 待处理记忆: {status['pending_count']} 条")
    
    else:
        print("使用 --help 查看集成命令选项")


def cleanup_command(args):
    """清理过期/低权重记忆"""
    memory_dir = Path(args.dir) if args.dir else Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    print("🧹 开始清理...")
    
    # 清理 SQLite 中的过期数据
    db_path = memory_dir / "layer2" / "memories.db"
    if db_path.exists():
        try:
            from memory_system.storage.sqlite_backend import SQLiteBackend
            backend = SQLiteBackend(memory_dir)
            deleted = backend.cleanup_expired()
            print(f"SQLite: 清理 {deleted} 条过期记录")
            backend.close()
        except Exception as e:
            print(f"⚠️ SQLite 清理失败：{e}")
    
    print("✅ 清理完成")


def list_command(args):
    """列出所有记忆"""
    memory_dir = Path(args.dir) if args.dir else Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = MemoryManager(memory_dir)
    records = manager.get_all()
    
    if not records:
        print("没有记忆")
        return
    
    print(f"\n共有 {len(records)} 条记忆:\n")
    for i, r in enumerate(records, 1):
        print(f"{i}. [{r.memory_type.value}] {r.content[:60]}... (置信度：{r.confidence:.2f})")


# === 多 Agent 命令 ===

def agent_register_command(args):
    """注册新 Agent"""
    if not MULTIAGENT_ENABLED:
        print("❌ 多 Agent 模块不可用")
        return
    
    memory_dir = Path(args.dir) if args.dir else Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = AgentManager(memory_dir)
    
    # 转换角色
    role_map = {
        "main": AgentRole.MAIN,
        "assistant": AgentRole.ASSISTANT,
        "specialist": AgentRole.SPECIALIST,
        "observer": AgentRole.OBSERVER,
    }
    role = role_map.get(args.role, AgentRole.ASSISTANT)
    
    agent_id = manager.register_agent(
        name=args.name,
        role=role,
        description=args.description or "",
        isolated_memory=not args.shared_memory,
    )
    
    print(f"✅ Agent 已注册")
    print(f"   ID: {agent_id}")
    print(f"   名称：{args.name}")
    print(f"   角色：{role.value}")
    print(f"   记忆隔离：{'是' if not args.shared_memory else '否'}")


def agent_list_command(args):
    """列出所有 Agent"""
    if not MULTIAGENT_ENABLED:
        print("❌ 多 Agent 模块不可用")
        return
    
    memory_dir = Path(args.dir) if args.dir else Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = AgentManager(memory_dir)
    agents = manager.list_agents()
    
    if not agents:
        print("没有已注册的 Agent")
        return
    
    print(f"\n共有 {len(agents)} 个 Agent:\n")
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent.name} ({agent.agent_id[:8]}...)")
        print(f"   角色：{agent.role.value}")
        print(f"   状态：{agent.status.value}")
        print(f"   记忆隔离：{'是' if agent.isolated_memory else '否'}")
        print()


def agent_status_command(args):
    """查看 Agent 状态"""
    if not MULTIAGENT_ENABLED:
        print("❌ 多 Agent 模块不可用")
        return
    
    memory_dir = Path(args.dir) if args.dir else Path.home() / ".openclaw" / "memory" / "openclaw-omg"
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = AgentManager(memory_dir)
    stats = manager.get_stats()
    
    print("📊 多 Agent 系统状态")
    print(f"\nAgent 统计:")
    print(f" - 总数：{stats['total_agents']}")
    print(f" - 活跃：{stats['active_agents']}")
    print(f" - 非活跃：{stats['inactive_agents']}")
    print(f" - 忙碌：{stats['busy_agents']}")
    
    if stats['roles']:
        print(f"\n角色分布:")
        for role, count in stats['roles'].items():
            print(f" - {role}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Memory System - AI Agent 持久化记忆系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("-v", "--version", action="version", version=f"Memory System v{__version__}")
    parser.add_argument("-d", "--dir", help="记忆系统目录（默认：./memory）")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # init
    p = subparsers.add_parser("init", help="初始化记忆系统")
    p.add_argument("--dir", help="记忆目录路径")
    p.set_defaults(func=init_command)
    
    # add
    p = subparsers.add_parser("add", help="添加记忆")
    p.add_argument("content", help="记忆内容")
    p.add_argument("--type", choices=["fact", "belief", "summary", "event"], default="fact")
    p.add_argument("--confidence", type=float, default=0.8)
    p.add_argument("--tags", help="标签（逗号分隔）")
    p.set_defaults(func=add_command)
    
    # capture - 即时捕获记忆
    p = subparsers.add_parser("capture", help="即时捕获记忆（自动评分）")
    p.add_argument("content", help="记忆内容")
    p.add_argument("--source", choices=["user", "assistant", "system"], default="user", help="来源")
    p.add_argument("--session", help="会话 ID")
    p.add_argument("--index", type=int, help="消息索引")
    p.set_defaults(func=capture_command)
    
    # search
    p = subparsers.add_parser("search", help="搜索记忆")
    p.add_argument("query", help="搜索关键词")
    p.add_argument("--top-k", type=int, default=10)
    p.set_defaults(func=search_command)
    
    # consolidate
    p = subparsers.add_parser("consolidate", help="执行记忆整合")
    p.set_defaults(func=consolidate_command)
    
    # status
    p = subparsers.add_parser("status", help="查看系统状态")
    p.set_defaults(func=status_command)
    
    # integration - OpenClaw 集成
    p = subparsers.add_parser("integration", help="OpenClaw 集成命令")
    p.add_argument("--inject", metavar="AGENT_ID", help="注入快照到 Agent")
    p.add_argument("--capture", nargs=3, metavar=("MSG", "SESSION", "INDEX"), help="捕获消息")
    p.add_argument("--consolidate", action="store_true", help="执行整合")
    p.add_argument("--cron", action="store_true", help="生成 Cron 配置")
    p.add_argument("--install-cron", action="store_true", help="安装 Cron 定时任务")
    p.add_argument("--status", action="store_true", help="查看集成状态")
    p.set_defaults(func=integration_command)
    
    # export
    p = subparsers.add_parser("export", help="导出记忆")
    p.add_argument("--output", "-o", help="输出文件路径")
    p.add_argument("--format", choices=["json", "csv"], default="json")
    p.set_defaults(func=export_command)
    
    # import
    p = subparsers.add_parser("import", help="导入记忆")
    p.add_argument("input", help="输入文件路径")
    p.set_defaults(func=import_command)
    
    # cleanup
    p = subparsers.add_parser("cleanup", help="清理过期数据")
    p.set_defaults(func=cleanup_command)
    
    # list
    p = subparsers.add_parser("list", help="列出所有记忆")
    p.set_defaults(func=list_command)
    
    # === 多 Agent 命令 ===
    if MULTIAGENT_ENABLED:
        # agent-register
        p = subparsers.add_parser("agent-register", help="注册新 Agent")
        p.add_argument("name", help="Agent 名称")
        p.add_argument("--role", choices=["main", "assistant", "specialist", "observer"], 
                       default="assistant", help="Agent 角色")
        p.add_argument("--description", "-d", help="Agent 描述")
        p.add_argument("--shared-memory", action="store_true", help="使用共享记忆空间")
        p.set_defaults(func=agent_register_command)
        
        # agent-list
        p = subparsers.add_parser("agent-list", help="列出所有 Agent")
        p.set_defaults(func=agent_list_command)
        
        # agent-status
        p = subparsers.add_parser("agent-status", help="查看 Agent 系统状态")
        p.set_defaults(func=agent_status_command)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == "__main__":
    main()
