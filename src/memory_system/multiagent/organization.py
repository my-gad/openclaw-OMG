#!/usr/bin/env python3
"""
组织架构管理 - Organization & Team Management

实现：
- 机构/团队的创建和嵌套
- 成员管理（Agent 加入/离开）
- 记忆共享规则（上层可看下层，下层不可看上层）
- 权限控制
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum


class OrgType(str, Enum):
    """组织类型"""
    ORGANIZATION = "organization"  # 机构（正式组织）
    TEAM = "team"  # 团队（项目组）


class MembershipStatus(str, Enum):
    """成员状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


@dataclass
class Organization:
    """组织/团队"""
    org_id: str
    name: str
    org_type: OrgType = OrgType.ORGANIZATION
    description: str = ""
    parent_id: Optional[str] = None  # 父组织 ID（支持嵌套）
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    created_by: Optional[str] = None  # 创建者 Agent ID
    
    # 成员列表
    members: Set[str] = field(default_factory=set)  # Agent IDs
    
    # 子组织
    child_orgs: Set[str] = field(default_factory=set)  # 子组织 IDs
    
    # 记忆空间
    shared_memory_space: Optional[str] = None  # 共享记忆空间 ID
    is_isolated: bool = True  # 是否默认隔离
    
    # 权限配置
    allow_parent_view: bool = True  # 允许父组织查看（默认开启）
    allow_child_inherit: bool = False  # 允许子组织继承（默认关闭）
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "org_id": self.org_id,
            "name": self.name,
            "org_type": self.org_type.value,
            "description": self.description,
            "parent_id": self.parent_id,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "members": list(self.members),
            "child_orgs": list(self.child_orgs),
            "shared_memory_space": self.shared_memory_space,
            "is_isolated": self.is_isolated,
            "allow_parent_view": self.allow_parent_view,
            "allow_child_inherit": self.allow_child_inherit,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Organization":
        return cls(
            org_id=data["org_id"],
            name=data["name"],
            org_type=OrgType(data.get("org_type", "organization")),
            description=data.get("description", ""),
            parent_id=data.get("parent_id"),
            created_at=data.get("created_at", datetime.now().timestamp()),
            created_by=data.get("created_by"),
            members=set(data.get("members", [])),
            child_orgs=set(data.get("child_orgs", [])),
            shared_memory_space=data.get("shared_memory_space"),
            is_isolated=data.get("is_isolated", True),
            allow_parent_view=data.get("allow_parent_view", True),
            allow_child_inherit=data.get("allow_child_inherit", False),
        )


@dataclass
class Membership:
    """成员资格"""
    agent_id: str
    org_id: str
    status: MembershipStatus = MembershipStatus.ACTIVE
    joined_at: float = field(default_factory=lambda: datetime.now().timestamp())
    role: str = "member"  # member, admin, creator
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "org_id": self.org_id,
            "status": self.status.value,
            "joined_at": self.joined_at,
            "role": self.role,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Membership":
        return cls(
            agent_id=data["agent_id"],
            org_id=data["org_id"],
            status=MembershipStatus(data.get("status", "active")),
            joined_at=data.get("joined_at", datetime.now().timestamp()),
            role=data.get("role", "member"),
            metadata=data.get("metadata", {}),
        )


class OrganizationManager:
    """
    组织管理器
    
    功能:
    - 创建/删除组织
    - 嵌套组织管理（树形结构）
    - 成员管理
    - 记忆共享控制
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = Path(memory_dir)
        self.orgs_dir = self.memory_dir / "organizations"
        self.orgs_dir.mkdir(parents=True, exist_ok=True)
        
        # 缓存
        self._organizations: Dict[str, Organization] = {}
        self._memberships: Dict[str, List[Membership]] = {}  # agent_id -> memberships
        
        # 加载已有组织
        self._load_organizations()
    
    def _load_organizations(self):
        """加载已有组织"""
        orgs_file = self.orgs_dir / "organizations.json"
        if orgs_file.exists():
            try:
                with open(orgs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for org_data in data:
                        self._organizations[org_data["org_id"]] = Organization.from_dict(org_data)
            except (json.JSONDecodeError, IOError):
                pass
        
        # 加载成员资格
        memberships_file = self.orgs_dir / "memberships.json"
        if memberships_file.exists():
            try:
                with open(memberships_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for m_data in data:
                        membership = Membership.from_dict(m_data)
                        agent_id = membership.agent_id
                        if agent_id not in self._memberships:
                            self._memberships[agent_id] = []
                        self._memberships[agent_id].append(membership)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_organizations(self):
        """保存组织列表"""
        orgs_file = self.orgs_dir / "organizations.json"
        data = [org.to_dict() for org in self._organizations.values()]
        with open(orgs_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_memberships(self):
        """保存成员资格"""
        memberships_file = self.orgs_dir / "memberships.json"
        data = []
        for memberships in self._memberships.values():
            for m in memberships:
                data.append(m.to_dict())
        with open(memberships_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create_organization(
        self,
        name: str,
        org_type: OrgType = OrgType.ORGANIZATION,
        description: str = "",
        parent_id: Optional[str] = None,
        creator_agent_id: Optional[str] = None,
        is_isolated: bool = True,
    ) -> str:
        """
        创建组织/团队
        
        Args:
            name: 组织名称
            org_type: 组织类型
            description: 描述
            parent_id: 父组织 ID（支持嵌套）
            creator_agent_id: 创建者 Agent ID
            is_isolated: 是否默认隔离
        
        Returns:
            组织 ID
        """
        org_id = str(uuid.uuid4())
        
        # 检查父组织是否存在
        if parent_id and parent_id not in self._organizations:
            raise ValueError(f"父组织不存在：{parent_id}")
        
        org = Organization(
            org_id=org_id,
            name=name,
            org_type=org_type,
            description=description,
            parent_id=parent_id,
            created_by=creator_agent_id,
            is_isolated=is_isolated,
        )
        
        self._organizations[org_id] = org
        
        # 添加到父组织的子组织列表
        if parent_id:
            parent_org = self._organizations[parent_id]
            parent_org.child_orgs.add(org_id)
        
        # 创建者自动成为成员和管理员
        if creator_agent_id:
            self.add_member(org_id, creator_agent_id, role="admin")
        
        self._save_organizations()
        
        return org_id
    
    def delete_organization(self, org_id: str) -> bool:
        """删除组织"""
        if org_id not in self._organizations:
            return False
        
        org = self._organizations[org_id]
        
        # 先删除所有子组织
        for child_id in list(org.child_orgs):
            self.delete_organization(child_id)
        
        # 从父组织中移除
        if org.parent_id and org.parent_id in self._organizations:
            parent_org = self._organizations[org.parent_id]
            parent_org.child_orgs.discard(org_id)
        
        del self._organizations[org_id]
        self._save_organizations()
        
        return True
    
    def get_organization(self, org_id: str) -> Optional[Organization]:
        """获取组织信息"""
        return self._organizations.get(org_id)
    
    def list_organizations(
        self,
        org_type: Optional[OrgType] = None,
        parent_id: Optional[str] = None,
    ) -> List[Organization]:
        """列出组织"""
        orgs = list(self._organizations.values())
        
        if org_type:
            orgs = [o for o in orgs if o.org_type == org_type]
        
        if parent_id is not None:
            if parent_id is None:
                orgs = [o for o in orgs if o.parent_id is None]
            else:
                orgs = [o for o in orgs if o.parent_id == parent_id]
        
        return orgs
    
    def add_member(
        self,
        org_id: str,
        agent_id: str,
        role: str = "member",
    ) -> bool:
        """添加成员到组织"""
        if org_id not in self._organizations:
            return False
        
        org = self._organizations[org_id]
        
        # 如果已是成员，更新状态
        if agent_id in org.members:
            # 更新现有成员资格
            if agent_id in self._memberships:
                for m in self._memberships[agent_id]:
                    if m.org_id == org_id:
                        m.status = MembershipStatus.ACTIVE
                        m.role = role
                        self._save_memberships()
                        return True
            return True
        
        # 添加新成员
        org.members.add(agent_id)
        
        membership = Membership(
            agent_id=agent_id,
            org_id=org_id,
            role=role,
        )
        
        if agent_id not in self._memberships:
            self._memberships[agent_id] = []
        self._memberships[agent_id].append(membership)
        
        self._save_organizations()
        self._save_memberships()
        
        return True
    
    def remove_member(self, org_id: str, agent_id: str) -> bool:
        """移除组织成员"""
        if org_id not in self._organizations:
            return False
        
        org = self._organizations[org_id]
        org.members.discard(agent_id)
        
        # 更新成员资格状态
        if agent_id in self._memberships:
            for m in self._memberships[agent_id]:
                if m.org_id == org_id:
                    m.status = MembershipStatus.INACTIVE
                    self._save_memberships()
                    break
        
        self._save_organizations()
        return True
    
    def get_member_orgs(self, agent_id: str) -> List[Organization]:
        """获取 Agent 所属的所有组织"""
        orgs = []
        if agent_id in self._memberships:
            for m in self._memberships[agent_id]:
                if m.status == MembershipStatus.ACTIVE and m.org_id in self._organizations:
                    orgs.append(self._organizations[m.org_id])
        return orgs
    
    def get_ancestor_orgs(self, org_id: str) -> List[Organization]:
        """获取祖先组织（父组织链）"""
        ancestors = []
        current_id = org_id
        
        while current_id and current_id in self._organizations:
            org = self._organizations[current_id]
            if org.parent_id and org.parent_id in self._organizations:
                parent = self._organizations[org.parent_id]
                ancestors.append(parent)
                current_id = org.parent_id
            else:
                break
        
        return ancestors
    
    def get_descendant_orgs(self, org_id: str) -> List[Organization]:
        """获取所有后代组织（递归）"""
        descendants = []
        
        if org_id not in self._organizations:
            return descendants
        
        org = self._organizations[org_id]
        
        for child_id in org.child_orgs:
            if child_id in self._organizations:
                child_org = self._organizations[child_id]
                descendants.append(child_org)
                descendants.extend(self.get_descendant_orgs(child_id))
        
        return descendants
    
    def can_view_memory(self, viewer_org_id: str, target_org_id: str) -> bool:
        """
        检查组织间记忆访问权限
        
        规则:
        - 同一组织内可以访问
        - 父组织可以查看子组织的非隔离记忆
        - 子组织不能查看父组织的记忆
        """
        if viewer_org_id == target_org_id:
            return True
        
        if viewer_org_id not in self._organizations:
            return False
        
        if target_org_id not in self._organizations:
            return False
        
        viewer_org = self._organizations[viewer_org_id]
        target_org = self._organizations[target_org_id]
        
        # 检查是否是祖先关系
        ancestors = self.get_ancestor_orgs(target_org_id)
        if viewer_org in ancestors:
            # 父组织查看子组织，需要子组织允许父组织查看
            return target_org.allow_parent_view
        
        return False
    
    def get_shared_memory_space(self, org_id: str) -> Optional[str]:
        """获取组织的共享记忆空间 ID"""
        if org_id not in self._organizations:
            return None
        
        org = self._organizations[org_id]
        return org.shared_memory_space
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "total_organizations": len(self._organizations),
            "organizations": 0,
            "teams": 0,
            "root_orgs": 0,
            "total_memberships": sum(len(m) for m in self._memberships.values()),
        }
        
        for org in self._organizations.values():
            if org.org_type == OrgType.ORGANIZATION:
                stats["organizations"] += 1
            else:
                stats["teams"] += 1
            
            if org.parent_id is None:
                stats["root_orgs"] += 1
        
        return stats
