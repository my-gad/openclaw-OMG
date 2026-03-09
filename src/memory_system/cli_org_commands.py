#!/usr/bin/env python3
"""
组织管理 CLI 命令（手动模式）

组织/团队必须手动创建，助手手动加入/退出
"""

from pathlib import Path
from memory_system.multiagent.organization import OrganizationManager, OrgType


def org_create_command(args):
    """手动创建组织/团队"""
    memory_dir = Path(args.dir) if hasattr(args, 'dir') and args.dir else Path("./memory")
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = OrganizationManager(memory_dir)
    
    # 转换组织类型
    org_type = OrgType.ORGANIZATION if getattr(args, 'type', 'org') == "org" else OrgType.TEAM
    
    org_id = manager.create_organization(
        name=args.name,
        org_type=org_type,
        description=getattr(args, 'description', ""),
        parent_id=getattr(args, 'parent', None),
        is_isolated=getattr(args, 'isolated', True),  # 默认隔离
    )
    
    print(f"✅ 组织已创建")
    print(f"   ID: {org_id}")
    print(f"   名称：{args.name}")
    print(f"   类型：{org_type.value}")
    if getattr(args, 'parent', None):
        print(f"   父组织：{args.parent}")
    print(f"   记忆隔离：{'是' if getattr(args, 'isolated', True) else '否'}")
    print(f"\n提示：创建后需要手动加入成员")
    print(f"  python3 -m memory_system.cli org-join {org_id} <Agent_ID>")


def org_list_command(args):
    """列出组织"""
    memory_dir = Path(args.dir) if hasattr(args, 'dir') and args.dir else Path("./memory")
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = OrganizationManager(memory_dir)
    orgs = manager.list_organizations()
    
    if not orgs:
        print("没有组织")
        print("\n提示：创建组织")
        print("  python3 -m memory_system.cli org-create \"组织名称\" --type org")
        return
    
    print(f"\n共有 {len(orgs)} 个组织:\n")
    for i, org in enumerate(orgs, 1):
        print(f"{i}. {org.name} ({org.org_id[:8]}...)")
        print(f"   类型：{org.org_type.value}")
        print(f"   成员：{len(org.members)} 人")
        print(f"   子组织：{len(org.child_orgs)} 个")
        print(f"   记忆隔离：{'是' if org.is_isolated else '否'}")
        if org.parent_id:
            print(f"   父组织：{org.parent_id[:8]}...")
        print()


def org_join_command(args):
    """手动加入组织"""
    memory_dir = Path(args.dir) if hasattr(args, 'dir') and args.dir else Path("./memory")
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = OrganizationManager(memory_dir)
    
    # 查找组织
    target_org = None
    for org in manager.list_organizations():
        if org.name == args.org_name or org.org_id == args.org_name:
            target_org = org
            break
    
    if not target_org:
        print(f"❌ 组织不存在：{args.org_name}")
        print("\n可用组织:")
        for org in manager.list_organizations():
            print(f"  - {org.name} ({org.org_id[:8]}...)")
        return
    
    result = manager.add_member(target_org.org_id, args.agent_id, role=getattr(args, 'role', 'member'))
    
    if result:
        print(f"✅ 已加入组织")
        print(f"   Agent: {args.agent_id}")
        print(f"   组织：{target_org.name} ({target_org.org_id[:8]}...)")
        print(f"   角色：{getattr(args, 'role', 'member')}")
    else:
        print("❌ 加入失败")


def org_leave_command(args):
    """手动退出组织"""
    memory_dir = Path(args.dir) if hasattr(args, 'dir') and args.dir else Path("./memory")
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = OrganizationManager(memory_dir)
    
    # 查找组织
    target_org = None
    for org in manager.list_organizations():
        if org.name == args.org_name or org.org_id == args.org_name:
            target_org = org
            break
    
    if not target_org:
        print(f"❌ 组织不存在：{args.org_name}")
        return
    
    result = manager.remove_member(target_org.org_id, args.agent_id)
    
    if result:
        print(f"✅ 已退出组织")
        print(f"   Agent: {args.agent_id}")
        print(f"   组织：{target_org.name}")
    else:
        print("❌ 退出失败")


def org_status_command(args):
    """查看组织系统状态"""
    memory_dir = Path(args.dir) if hasattr(args, 'dir') and args.dir else Path("./memory")
    if not memory_dir.exists():
        print("❌ 记忆系统未初始化")
        return
    
    manager = OrganizationManager(memory_dir)
    stats = manager.get_stats()
    
    print("📊 组织系统状态")
    print(f"\n组织统计:")
    print(f" - 总组织数：{stats['total_organizations']}")
    print(f" - 机构数：{stats['organizations']}")
    print(f" - 团队数：{stats['teams']}")
    print(f" - 根组织：{stats['root_orgs']}")
    print(f" - 总成员资格：{stats['total_memberships']}")
    
    # 显示组织树
    print(f"\n组织树:")
    root_orgs = [o for o in manager.list_organizations() if o.parent_id is None]
    for org in root_orgs:
        _print_org_tree(org, manager, 0)


def _print_org_tree(org, manager, level=0):
    """递归打印组织树"""
    indent = "  " * level
    print(f"{indent}- {org.name} ({org.org_id[:8]}...) - {len(org.members)} 成员")
    
    for child_id in org.child_orgs:
        if child_id in manager._organizations:
            child_org = manager._organizations[child_id]
            _print_org_tree(child_org, manager, level + 1)
