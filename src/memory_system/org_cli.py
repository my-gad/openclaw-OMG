#!/usr/bin/env python3
"""
组织管理 CLI - 手动模式

组织/团队必须手动创建，助手手动加入/退出
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from memory_system.cli_org_commands import org_create_command, org_list_command, org_join_command, org_leave_command, org_status_command


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="组织管理 CLI")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # org-create
    p = subparsers.add_parser("create", help="创建组织/团队")
    p.add_argument("name", help="组织名称")
    p.add_argument("--type", choices=["org", "team"], default="org", help="组织类型")
    p.add_argument("--description", "-d", help="组织描述")
    p.add_argument("--parent", help="父组织 ID")
    p.add_argument("--isolated", action="store_true", help="记忆隔离（默认）")
    p.set_defaults(func=org_create_command)
    
    # org-list
    p = subparsers.add_parser("list", help="列出所有组织")
    p.set_defaults(func=org_list_command)
    
    # org-join
    p = subparsers.add_parser("join", help="加入组织")
    p.add_argument("org_name", help="组织名称或 ID")
    p.add_argument("agent_id", help="Agent ID")
    p.add_argument("--role", default="member", help="角色（默认：member）")
    p.set_defaults(func=org_join_command)
    
    # org-leave
    p = subparsers.add_parser("leave", help="退出组织")
    p.add_argument("org_name", help="组织名称或 ID")
    p.add_argument("agent_id", help="Agent ID")
    p.set_defaults(func=org_leave_command)
    
    # org-status
    p = subparsers.add_parser("status", help="查看组织系统状态")
    p.set_defaults(func=org_status_command)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == "__main__":
    main()
