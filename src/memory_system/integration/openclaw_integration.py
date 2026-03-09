#!/usr/bin/env python3
"""
OpenClaw 集成模块

功能：
- Layer 1 快照自动注入到 systemPrompt
- 会话 Hook 自动捕获记忆
- Cron 定时任务配置
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


# 路径配置
# Skill 目录 - 代码位置
SKILL_DIR = Path(__file__).parent.parent.parent.parent
# 记忆目录 - 独立存储，卸载 Skill 不丢失
OPENCLAW_MEMORY_DIR = Path.home() / ".openclaw" / "memory" / "openclaw-omg"
OPENCLAW_CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"


def get_openclaw_config() -> Dict:
    """获取 OpenClaw 配置"""
    if not OPENCLAW_CONFIG_PATH.exists():
        return {}
    with open(OPENCLAW_CONFIG_PATH, 'r') as f:
        return json.load(f)


def get_snapshot_for_injection() -> str:
    """
    获取用于注入 systemPrompt 的快照内容
    """
    from memory_system.core.snapshot_generator import get_snapshot_for_prompt
    
    snapshot = get_snapshot_for_prompt(OPENCLAW_MEMORY_DIR)
    return snapshot


def inject_to_system_prompt(agent_id: str) -> bool:
    """
    将快照注入到 Agent 的 systemPrompt
    
    Args:
        agent_id: Agent ID
    
    Returns:
        是否成功
    """
    try:
        snapshot = get_snapshot_for_injection()
        
        # 读取 Agent 目录的 systemPrompt 文件
        agent_dir = Path.home() / ".openclaw" / "agents" / agent_id / "agent"
        prompt_file = agent_dir / "PROMPT.md"
        
        if not prompt_file.exists():
            # 尝试其他位置
            prompt_file = agent_dir / "system_prompt.md"
        
        if prompt_file.exists():
            content = prompt_file.read_text(encoding='utf-8')
            
            # 检查是否已有快照标记
            if "# 工作记忆快照" in content:
                # 更新现有快照
                lines = content.split('\n')
                start = -1
                end = -1
                for i, line in enumerate(lines):
                    if line.startswith("# 工作记忆快照"):
                        start = i
                    if start > 0 and line.startswith("---") and i > start:
                        end = i
                        break
                
                if start > 0 and end > 0:
                    lines = lines[:start] + snapshot.split('\n') + lines[end:]
                    content = '\n'.join(lines)
            else:
                # 追加快照
                content = content + "\n\n---\n\n" + snapshot
            
            prompt_file.write_text(content, encoding='utf-8')
            return True
        
        return False
    except Exception as e:
        print(f"注入失败: {e}")
        return False


def capture_from_message(
    message: str,
    session_id: str,
    message_index: int,
    source: str = "user"
) -> Dict:
    """
    从消息捕获记忆
    
    Args:
        message: 消息内容
        session_id: 会话 ID
        message_index: 消息索引
        source: 来源 (user/assistant)
    
    Returns:
        捕获结果
    """
    try:
        result = subprocess.run(
            [
                "python3", "-m", "memory_system.cli",
                "capture", message,
                "--source", source,
                "--session", session_id,
                "--index", str(message_index),
            ],
            cwd=str(OPENCLAW_MEMORY_DIR.parent),
            env={**os.environ, "PYTHONPATH": str(OPENCLAW_MEMORY_DIR.parent / "src")},
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def run_consolidation() -> Dict:
    """
    执行记忆整合
    
    Returns:
        执行结果
    """
    try:
        result = subprocess.run(
            ["python3", "-m", "memory_system.cli", "consolidate"],
            cwd=str(OPENCLAW_MEMORY_DIR.parent),
            env={**os.environ, "PYTHONPATH": str(OPENCLAW_MEMORY_DIR.parent / "src")},
            capture_output=True,
            text=True,
            timeout=300,
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def generate_cron_config() -> str:
    """
    生成 Cron 配置
    
    Returns:
        Crontab 配置行
    """
    # 每天凌晨 3 点执行 Consolidation
    cron_line = "0 3 * * * cd {} && PYTHONPATH=src python3 -m memory_system.cli consolidate >> /tmp/omg_consolidation.log 2>&1".format(
        OPENCLAW_MEMORY_DIR.parent
    )
    
    return f"""
# OMG 记忆系统定时任务
# 每天凌晨 3 点执行记忆整合
{cron_line}

# 每小时更新快照
0 * * * * cd {OPENCLAW_MEMORY_DIR.parent} && PYTHONPATH=src python3 -c "from memory_system.core.snapshot_generator import update_snapshot; update_snapshot('{OPENCLAW_MEMORY_DIR}')" >> /tmp/omg_snapshot.log 2>&1
"""


def install_cron():
    """安装 Cron 定时任务"""
    cron_config = generate_cron_config()
    
    # 读取现有 crontab
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""
    
    # 添加 OMG 任务
    if "# OMG 记忆系统" not in existing:
        new_cron = existing + "\n" + cron_config
        subprocess.run(["crontab", "-"], input=new_cron, text=True)
        return True
    
    return False


def get_integration_status() -> Dict:
    """获取集成状态"""
    status = {
        "openclaw_config_exists": OPENCLAW_CONFIG_PATH.exists(),
        "memory_dir_exists": OPENCLAW_MEMORY_DIR.exists(),
        "snapshot_available": False,
        "pending_count": 0,
    }
    
    if status["memory_dir_exists"]:
        from memory_system.core.memory_capture import get_pending_count
        status["pending_count"] = get_pending_count(OPENCLAW_MEMORY_DIR)
        
        snapshot_path = OPENCLAW_MEMORY_DIR / "layer1" / "snapshot.md"
        status["snapshot_available"] = snapshot_path.exists()
    
    return status


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OpenClaw 集成")
    parser.add_argument("--inject", help="注入快照到 Agent")
    parser.add_argument("--capture", nargs=3, metavar=("MSG", "SESSION", "INDEX"), help="捕获消息")
    parser.add_argument("--consolidate", action="store_true", help="执行整合")
    parser.add_argument("--cron", action="store_true", help="生成 Cron 配置")
    parser.add_argument("--status", action="store_true", help="查看状态")
    
    args = parser.parse_args()
    
    if args.inject:
        inject_to_system_prompt(args.inject)
    elif args.capture:
        capture_from_message(args.capture[0], args.capture[1], int(args.capture[2]))
    elif args.consolidate:
        run_consolidation()
    elif args.cron:
        print(generate_cron_config())
    elif args.status:
        print(json.dumps(get_integration_status(), indent=2))
