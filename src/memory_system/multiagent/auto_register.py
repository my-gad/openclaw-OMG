#!/usr/bin/env python3
"""
自动注册模块 - Auto Registration

功能：
- 检测当前 Agent 是否已注册
- 未注册时自动完成注册
- 支持环境变量配置
- 支持默认组织归属
"""

import os
import json
import uuid
import socket
import getpass
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from memory_system.multiagent.agent_manager import AgentManager, AgentRole, AgentStatus
from memory_system.multiagent.organization import OrganizationManager, OrgType


# 环境变量配置
ENV_AGENT_NAME = "OPENCLAW_AGENT_NAME"
ENV_AGENT_ROLE = "OPENCLAW_AGENT_ROLE"
ENV_AGENT_DESC = "OPENCLAW_AGENT_DESCRIPTION"
ENV_DEFAULT_ORG = "OPENCLAW_DEFAULT_ORG"
ENV_AUTO_JOIN = "OPENCLAW_AUTO_JOIN"
ENV_MEMORY_DIR = "OPENCLAW_MEMORY_DIR"
ENV_OPENCLAW_CONFIG = "OPENCLAW_CONFIG_PATH"


def load_openclaw_agents() -> Dict[str, Dict]:
    """
    从 OpenClaw 主配置读取 Agent 列表
    
    Returns:
        {agent_id: {name, role, workspace, ...}}
    """
    # 查找配置文件
    config_paths = [
        os.path.expanduser("~/.openclaw/openclaw.json"),
        os.path.expanduser("~/.config/openclaw/openclaw.json"),
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                agents = {}
                agents_config = config.get("agents", {})
                agent_list = agents_config.get("list", []) if isinstance(agents_config, dict) else []
                
                for agent in agent_list:
                    agent_id = agent.get("id", "")
                    if agent_id:
                        # 映射 role - main 角色用 main，其他用 assistant
                        role = "main" if agent_id == "main" else "assistant"
                        
                        # 清理名称（去除空格）
                        name = agent.get("name", agent_id).replace(" ", "")
                        
                        agents[agent_id] = {
                            "name": name,
                            "role": role,
                            "workspace": agent.get("workspace", ""),
                            "model": agent.get("model", {}).get("primary", "") if isinstance(agent.get("model"), dict) else str(agent.get("model", "")),
                        }
                
                if agents:
                    return agents
            except Exception as e:
                print(f"Warning: 读取 OpenClaw 配置失败: {e}")
    
    return {}


# 缓存 OpenClaw Agent 配置
OPENCLAW_AGENTS = load_openclaw_agents()


def get_current_agent_identity() -> Tuple[str, str, str]:
    """
    获取当前 Agent 的身份信息
    
    优先级：
    1. 环境变量 (OPENCLAW_AGENT_NAME)
    2. OpenClaw 主配置 (~/.openclaw/openclaw.json)
    3. 系统默认值
    
    Returns:
        (agent_name, agent_role, description)
    """
    # 1. 优先从环境变量获取
    agent_name = os.getenv(ENV_AGENT_NAME, "")
    agent_role = os.getenv(ENV_AGENT_ROLE, "")
    agent_desc = os.getenv(ENV_AGENT_DESC, "")
    
    # 2. 如果环境变量没有，尝试从 OpenClaw 配置获取
    if not agent_name and OPENCLAW_AGENTS:
        # 尝试从当前进程或环境获取 agent_id
        # 检查常见的 OpenClaw 环境变量
        current_agent_id = os.getenv("OPENCLAW_CURRENT_AGENT", os.getenv("AGENT_ID", ""))
        
        if current_agent_id and current_agent_id in OPENCLAW_AGENTS:
            oc_agent = OPENCLAW_AGENTS[current_agent_id]
            agent_name = oc_agent["name"]
            agent_role = oc_agent.get("role", "assistant")
            agent_desc = f"OpenClaw Agent - {oc_agent.get('model', '')}"
        elif OPENCLAW_AGENTS:
            # 如果没有指定，使用第一个 Agent
            first_id = list(OPENCLAW_AGENTS.keys())[0]
            oc_agent = OPENCLAW_AGENTS[first_id]
            agent_name = oc_agent["name"]
            agent_role = oc_agent.get("role", "assistant")
            agent_desc = f"OpenClaw Agent - {oc_agent.get('model', '')}"
    
    # 3. 如果都没有，使用默认值
    if not agent_name:
        username = getpass.getuser()
        hostname = socket.gethostname()
        agent_name = f"{username}@{hostname}"
        agent_role = "assistant"
    
    if not agent_desc:
        agent_desc = f"自动注册的 Agent - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    return agent_name, agent_role, agent_desc


def get_or_create_agent(
    memory_dir: Optional[Path] = None,
    agent_name: Optional[str] = None,
    agent_role: Optional[str] = None,
    description: Optional[str] = None,
    auto_join_org: Optional[str] = None,
    isolated_memory: bool = True,
) -> Tuple[str, bool]:
    """
    获取或创建当前 Agent
    
    Args:
        memory_dir: 记忆目录
        agent_name: Agent 名称（可选，从环境变量获取）
        agent_role: Agent 角色（可选，从环境变量获取）
        description: 描述（可选，从环境变量获取）
        auto_join_org: 自动加入的组织 ID（可选）
        isolated_memory: 是否使用独立记忆空间
    
    Returns:
        (agent_id, is_new) - agent_id 和是否为新注册
    """
    if memory_dir is None:
        memory_dir = Path(os.getenv(ENV_MEMORY_DIR, "./memory"))
    elif isinstance(memory_dir, str):
        memory_dir = Path(memory_dir)
    
    # 初始化 Agent 管理器
    agent_manager = AgentManager(memory_dir)
    
    # 获取当前 Agent 身份
    current_name, current_role, current_desc = get_current_agent_identity()
    
    # 使用传入的参数覆盖
    if agent_name:
        current_name = agent_name
    if agent_role:
        current_role = agent_role
    if description:
        current_desc = description
    
    # 转换角色
    role_map = {
        "main": AgentRole.MAIN,
        "assistant": AgentRole.ASSISTANT,
        "specialist": AgentRole.SPECIALIST,
        "observer": AgentRole.OBSERVER,
    }
    role = role_map.get(current_role.lower(), AgentRole.ASSISTANT)
    
    # 查找是否已存在同名的 Agent
    existing_agent = None
    for agent in agent_manager.list_agents():
        if agent.name == current_name:
            existing_agent = agent
            break
    
    if existing_agent:
        # Agent 已存在，更新状态为活跃
        agent_manager.update_agent_status(existing_agent.agent_id, AgentStatus.ACTIVE)
        return existing_agent.agent_id, False
    
    # 注册新 Agent
    agent_id = agent_manager.register_agent(
        name=current_name,
        role=role,
        description=current_desc,
        isolated_memory=isolated_memory,
    )
    
    # 如果指定了组织，自动加入
    if auto_join_org:
        org_manager = OrganizationManager(memory_dir)
        if auto_join_org in org_manager._organizations:
            org_manager.add_member(auto_join_org, agent_id, role="member")
    
    return agent_id, True


def ensure_agent_in_org(
    agent_id: str,
    org_name: str,
    memory_dir: Optional[Path] = None,
    create_if_missing: bool = False,  # 默认不自动创建
) -> bool:
    """
    确保 Agent 在指定组织中
    
    Args:
        agent_id: Agent ID
        org_name: 组织名称
        memory_dir: 记忆目录
        create_if_missing: 如果组织不存在是否创建（默认 False）
    
    Returns:
        是否成功加入
    """
    if memory_dir is None:
        memory_dir = Path(os.getenv(ENV_MEMORY_DIR, "./memory"))
    elif isinstance(memory_dir, str):
        memory_dir = Path(memory_dir)
    
    org_manager = OrganizationManager(memory_dir)
    
    # 查找同名组织
    target_org = None
    for org in org_manager.list_organizations():
        if org.name == org_name:
            target_org = org
            break
    
    # 组织不存在时不自动创建
    if not target_org:
        print(f"⚠️ 组织不存在：{org_name}")
        print(f"   请先创建组织：python3 -m memory_system.cli org-create \"{org_name}\"")
        return False
    
    # 加入组织
    return org_manager.add_member(target_org.org_id, agent_id, role="member")


def quick_setup(
    agent_name: Optional[str] = None,
    org_name: Optional[str] = None,
    parent_org_name: Optional[str] = None,
    memory_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    一键快速设置
    
    自动完成：
    1. 检测/注册 Agent
    2. 检测/创建组织
    3. 加入组织
    
    Args:
        agent_name: Agent 名称（可选）
        org_name: 组织名称（可选）
        parent_org_name: 父组织名称（可选）
        memory_dir: 记忆目录
    
    Returns:
        包含 agent_id, org_id, is_new 等信息
    """
    if memory_dir is None:
        memory_dir = Path(os.getenv(ENV_MEMORY_DIR, "./memory"))
    elif isinstance(memory_dir, str):
        memory_dir = Path(memory_dir)
    
    # 1. 获取或创建 Agent
    agent_id, is_new = get_or_create_agent(
        memory_dir=memory_dir,
        agent_name=agent_name,
    )
    
    result = {
        "agent_id": agent_id,
        "is_new": is_new,
        "org_id": None,
    }
    
    # 2. 如果指定了组织，确保加入
    if org_name:
        # 查找父组织
        parent_id = None
        if parent_org_name:
            org_manager = OrganizationManager(memory_dir)
            for org in org_manager.list_organizations():
                if org.name == parent_org_name:
                    parent_id = org.org_id
                    break
        
        # 确保在组织中
        if ensure_agent_in_org(
            agent_id,
            org_name,
            memory_dir=memory_dir,
            create_if_missing=True,
            parent_org=parent_id,
        ):
            # 获取组织 ID
            org_manager = OrganizationManager(memory_dir)
            for org in org_manager.list_organizations():
                if org.name == org_name and agent_id in org.members:
                    result["org_id"] = org.org_id
                    break
    
    return result


def auto_register_cli():
    """CLI 入口 - 自动注册当前 Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自动注册当前 Agent")
    parser.add_argument("--name", help="Agent 名称")
    parser.add_argument("--org", help="加入的组织名称")
    parser.add_argument("--parent-org", help="父组织名称")
    parser.add_argument("--dir", help="记忆目录", default="./memory")
    
    args = parser.parse_args()
    
    memory_dir = Path(args.dir)
    
    result = quick_setup(
        agent_name=args.name,
        org_name=args.org,
        parent_org_name=getattr(args, 'parent_org', None),
        memory_dir=memory_dir,
    )
    
    if result["is_new"]:
        print(f"✅ 已自动注册新 Agent")
    else:
        print(f"✓ Agent 已存在")
    
    print(f"   Agent ID: {result['agent_id']}")
    
    if result["org_id"]:
        print(f"   已加入组织：{result['org_id']}")
    elif args.org:
        print(f"   ⚠️ 加入组织失败")
    
    print(f"\n提示：将此命令添加到启动脚本实现自动注册")
    print(f"  python3 -m memory_system.multiagent.auto_register --name '我的 Agent' --org '我的团队'")


if __name__ == "__main__":
    auto_register_cli()
