#!/usr/bin/env python3
"""
自动注册模块 - Auto Registration

功能：
- 检测当前 Agent 是否已注册
- 未注册时自动完成注册
- 从 OpenClaw 主配置读取 Agent 列表
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from memory_system.multiagent.agent_manager import AgentManager, AgentRole, AgentStatus
from memory_system.multiagent.organization import OrganizationManager, OrgType


# OpenClaw 配置文件路径
OPENCLAW_CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"


def load_openclaw_agents() -> Dict[str, Dict]:
    """
    从 OpenClaw 主配置读取 Agent 列表
    
    Returns:
        {agent_id: {name, role, workspace, ...}}
    """
    if not OPENCLAW_CONFIG_PATH.exists():
        return {}
    
    try:
        with open(OPENCLAW_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        agents = {}
        agents_config = config.get("agents", {})
        agent_list = agents_config.get("list", []) if isinstance(agents_config, dict) else []
        
        for agent in agent_list:
            agent_id = agent.get("id", "")
            if agent_id:
                role = "main" if agent_id == "main" else "assistant"
                name = agent.get("name", agent_id).replace(" ", "")
                
                agents[agent_id] = {
                    "name": name,
                    "role": role,
                    "workspace": agent.get("workspace", ""),
                    "model": agent.get("model", {}).get("primary", "") if isinstance(agent.get("model"), dict) else str(agent.get("model", "")),
                }
        
        return agents
    except Exception:
        return {}


# 缓存 OpenClaw Agent 配置
OPENCLAW_AGENTS = load_openclaw_agents()


def get_current_agent_identity(agent_id: Optional[str] = None) -> Tuple[str, str, str]:
    """
    获取当前 Agent 的身份信息
    
    Args:
        agent_id: 指定 Agent ID，默认从 OpenClaw 配置获取第一个
    
    Returns:
        (agent_name, agent_role, description)
    """
    # 从 OpenClaw 配置获取
    if agent_id and agent_id in OPENCLAW_AGENTS:
        oc_agent = OPENCLAW_AGENTS[agent_id]
        return (
            oc_agent["name"],
            oc_agent.get("role", "assistant"),
            f"OpenClaw Agent - {oc_agent.get('model', '')}"
        )
    
    # 使用第一个 Agent
    if OPENCLAW_AGENTS:
        first_id = list(OPENCLAW_AGENTS.keys())[0]
        oc_agent = OPENCLAW_AGENTS[first_id]
        return (
            oc_agent["name"],
            oc_agent.get("role", "assistant"),
            f"OpenClaw Agent - {oc_agent.get('model', '')}"
        )
    
    # 默认值
    return "未命名 Agent", "assistant", f"自动注册 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"


def get_or_create_agent(
    memory_dir: Optional[Path] = None,
    agent_name: Optional[str] = None,
    agent_role: Optional[str] = None,
    description: Optional[str] = None,
    auto_join_org: Optional[str] = None,
    isolated_memory: bool = True,
    agent_id: Optional[str] = None,
) -> Tuple[str, bool]:
    """
    获取或创建当前 Agent
    
    Args:
        memory_dir: 记忆目录
        agent_name: Agent 名称（可选）
        agent_role: Agent 角色（可选）
        description: 描述（可选）
        auto_join_org: 自动加入的组织 ID（可选）
        isolated_memory: 是否使用独立记忆空间
        agent_id: 指定 Agent ID（从 OpenClaw 配置读取）
    
    Returns:
        (agent_id, is_new) - agent_id 和是否为新注册
    """
    if memory_dir is None:
        memory_dir = Path("./memory")
    elif isinstance(memory_dir, str):
        memory_dir = Path(memory_dir)
    
    agent_manager = AgentManager(memory_dir)
    
    # 获取当前 Agent 身份
    current_name, current_role, current_desc = get_current_agent_identity(agent_id)
    
    if agent_name:
        current_name = agent_name
    if agent_role:
        current_role = agent_role
    if description:
        current_desc = description
    
    role_map = {
        "main": AgentRole.MAIN,
        "assistant": AgentRole.ASSISTANT,
        "specialist": AgentRole.SPECIALIST,
        "observer": AgentRole.OBSERVER,
    }
    role = role_map.get(current_role.lower(), AgentRole.ASSISTANT)
    
    # 优先使用指定的 agent_id
    target_agent_id = agent_id
    
    # 如果没有指定，查找同名 Agent
    if not target_agent_id:
        for agent in agent_manager.list_agents():
            if agent.name == current_name:
                target_agent_id = agent.agent_id
                break
    
    if target_agent_id:
        # Agent 已存在，更新状态
        try:
            agent_manager.update_agent_status(target_agent_id, AgentStatus.ACTIVE)
        except Exception:
            pass
        return target_agent_id, False
    
    # 注册新 Agent
    agent_id_new = agent_manager.register_agent(
        name=current_name,
        role=role,
        description=current_desc,
        isolated_memory=isolated_memory,
    )
    
    if auto_join_org:
        org_manager = OrganizationManager(memory_dir)
        if auto_join_org in org_manager._organizations:
            org_manager.add_member(auto_join_org, agent_id_new, role="member")
    
    return agent_id_new, True


def ensure_agent_in_org(
    agent_id: str,
    org_name: str,
    memory_dir: Optional[Path] = None,
    create_if_missing: bool = False,
) -> bool:
    """确保 Agent 在指定组织中"""
    if memory_dir is None:
        memory_dir = Path("./memory")
    elif isinstance(memory_dir, str):
        memory_dir = Path(memory_dir)
    
    org_manager = OrganizationManager(memory_dir)
    
    target_org = None
    for org in org_manager.list_organizations():
        if org.name == org_name:
            target_org = org
            break
    
    if not target_org:
        print(f"⚠️ 组织不存在：{org_name}")
        return False
    
    return org_manager.add_member(target_org.org_id, agent_id, role="member")


def quick_setup(
    agent_name: Optional[str] = None,
    org_name: Optional[str] = None,
    parent_org_name: Optional[str] = None,
    memory_dir: Optional[Path] = None,
    agent_id: Optional[str] = None,
) -> Dict[str, Any]:
    """一键快速设置"""
    if memory_dir is None:
        memory_dir = Path("./memory")
    elif isinstance(memory_dir, str):
        memory_dir = Path(memory_dir)
    
    agent_id, is_new = get_or_create_agent(
        memory_dir=memory_dir,
        agent_name=agent_name,
        agent_id=agent_id,
    )
    
    result = {
        "agent_id": agent_id,
        "is_new": is_new,
        "org_id": None,
    }
    
    if org_name:
        parent_id = None
        if parent_org_name:
            org_manager = OrganizationManager(memory_dir)
            for org in org_manager.list_organizations():
                if org.name == parent_org_name:
                    parent_id = org.org_id
                    break
        
        if ensure_agent_in_org(agent_id, org_name, memory_dir=memory_dir, create_if_missing=True):
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
    parser.add_argument("--id", help="Agent ID")
    parser.add_argument("--org", help="加入的组织名称")
    parser.add_argument("--dir", help="记忆目录", default="./memory")
    
    args = parser.parse_args()
    
    memory_dir = Path(args.dir)
    
    result = quick_setup(
        agent_name=args.name,
        org_name=args.org,
        memory_dir=memory_dir,
        agent_id=args.id,
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


if __name__ == "__main__":
    auto_register_cli()
