"""
Multi-Agent - 多 Agent 支持模块

提供多 Agent 管理、Agent 间通信、记忆隔离、组织架构等功能。
"""

from memory_system.multiagent.agent_manager import (
    AgentManager,
    AgentConfig,
    AgentMessage,
    AgentStatus,
    AgentRole,
)

from memory_system.multiagent.organization import (
    OrganizationManager,
    Organization,
    OrgType,
    Membership,
    MembershipStatus,
)

__all__ = [
    "AgentManager",
    "AgentConfig",
    "AgentMessage",
    "AgentStatus",
    "AgentRole",
    "OrganizationManager",
    "Organization",
    "OrgType",
    "Membership",
    "MembershipStatus",
]
