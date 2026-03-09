#!/usr/bin/env python3
"""
Memory System Auto Start - 自动启动和注册

在助手启动时自动调用，完成：
1. 检测并自动注册当前 Agent
2. 自动加入默认组织
3. 初始化记忆系统
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# 自动注册模块
from memory_system.multiagent.auto_register import (
    quick_setup,
    get_or_create_agent,
    ensure_agent_in_org,
    ENV_DEFAULT_ORG,
    ENV_AUTO_JOIN,
    ENV_MEMORY_DIR,
)


def auto_start(
    agent_name: Optional[str] = None,
    default_org: Optional[str] = None,
    memory_dir: Optional[Path] = None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    自动启动并注册
    
    Args:
        agent_name: Agent 名称（可选，从环境变量获取）
        default_org: 默认组织名称（可选，从环境变量获取）
        memory_dir: 记忆目录
        verbose: 是否输出详细信息
    
    Returns:
        包含注册信息的字典
    """
    result = {
        "success": False,
        "agent_id": None,
        "is_new": False,
        "org_id": None,
        "message": "",
    }
    
    try:
        # 获取记忆目录
        if memory_dir is None:
            memory_dir = Path(os.getenv(ENV_MEMORY_DIR, "./memory"))
        elif isinstance(memory_dir, str):
            memory_dir = Path(memory_dir)
        
        # 获取默认组织
        if default_org is None:
            default_org = os.getenv(ENV_DEFAULT_ORG, "")
        
        # 1. 获取或创建 Agent
        agent_id, is_new = get_or_create_agent(
            memory_dir=memory_dir,
            agent_name=agent_name,
        )
        
        result["agent_id"] = agent_id
        result["is_new"] = is_new
        
        if verbose:
            if is_new:
                print(f"✅ 已自动注册 Agent: {agent_id[:8]}...")
            else:
                print(f"✓ Agent 已存在：{agent_id[:8]}...")
        
        # 2. 如果指定了默认组织，确保加入
        if default_org:
            from memory_system.multiagent.organization import OrganizationManager
            
            org_manager = OrganizationManager(memory_dir)
            
            # 查找组织
            target_org = None
            for org in org_manager.list_organizations():
                if org.name == default_org:
                    target_org = org
                    break
            
            if target_org:
                # 加入组织
                org_manager.add_member(target_org.org_id, agent_id, role="member")
                result["org_id"] = target_org.org_id
                
                if verbose:
                    print(f"✓ 已加入组织：{default_org}")
            else:
                # 组织不存在，创建它
                if os.getenv(ENV_AUTO_JOIN, "true").lower() == "true":
                    org_id = org_manager.create_organization(
                        name=default_org,
                        org_type="team",
                        description="默认组织（自动创建）",
                        is_isolated=False,
                    )
                    org_manager.add_member(org_id, agent_id, role="member")
                    result["org_id"] = org_id
                    
                    if verbose:
                        print(f"✅ 已创建并加入组织：{default_org}")
        
        result["success"] = True
        result["message"] = "自动启动完成"
        
    except Exception as e:
        result["success"] = False
        result["message"] = str(e)
        
        if verbose:
            print(f"⚠️ 自动启动失败：{e}")
    
    return result


def quick_start(agent_name: Optional[str] = None):
    """
    快速启动（最简单的方式）
    
    自动从环境变量读取配置，无需任何参数
    """
    return auto_start(
        agent_name=agent_name,
        verbose=True,
    )


# 命令行入口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory System 自动启动")
    parser.add_argument("--name", help="Agent 名称")
    parser.add_argument("--org", help="默认组织")
    parser.add_argument("--dir", help="记忆目录", default="./memory")
    parser.add_argument("--quiet", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    result = auto_start(
        agent_name=args.name,
        default_org=args.org,
        memory_dir=Path(args.dir),
        verbose=not args.quiet,
    )
    
    if not result["success"]:
        sys.exit(1)
