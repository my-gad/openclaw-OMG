#!/usr/bin/env python3
"""
Multi-Agent Manager - 多 Agent 管理器

支持：
- Agent 注册和注销
- Agent 身份管理
- Agent 内存隔离
- Agent 间通信
- 共享记忆空间
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum


class AgentStatus(str, Enum):
    """Agent 状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"


class AgentRole(str, Enum):
    """Agent 角色"""
    MAIN = "main"           # 主 Agent
    ASSISTANT = "assistant" # 助手 Agent
    SPECIALIST = "specialist"  # 专家 Agent
    OBSERVER = "observer"   # 观察者


@dataclass
class AgentConfig:
    """Agent 配置"""
    agent_id: str
    name: str
    role: AgentRole = AgentRole.ASSISTANT
    description: str = ""
    status: AgentStatus = AgentStatus.INACTIVE
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    last_active: float = field(default_factory=lambda: datetime.now().timestamp())
    
    # 内存隔离配置
    isolated_memory: bool = True  # 是否使用独立记忆空间
    shared_memory_spaces: Set[str] = field(default_factory=set)  # 共享记忆空间
    
    # 通信配置
    can_send_messages: bool = True
    can_receive_messages: bool = True
    allowed_agents: Set[str] = field(default_factory=set)  # 允许通信的 Agent
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "isolated_memory": self.isolated_memory,
            "shared_memory_spaces": list(self.shared_memory_spaces),
            "can_send_messages": self.can_send_messages,
            "can_receive_messages": self.can_receive_messages,
            "allowed_agents": list(self.allowed_agents),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            role=AgentRole(data.get("role", "assistant")),
            description=data.get("description", ""),
            status=AgentStatus(data.get("status", "inactive")),
            created_at=data.get("created_at", datetime.now().timestamp()),
            last_active=data.get("last_active", datetime.now().timestamp()),
            isolated_memory=data.get("isolated_memory", True),
            shared_memory_spaces=set(data.get("shared_memory_spaces", [])),
            can_send_messages=data.get("can_send_messages", True),
            can_receive_messages=data.get("can_receive_messages", True),
            allowed_agents=set(data.get("allowed_agents", [])),
        )


@dataclass
class AgentMessage:
    """Agent 间消息"""
    message_id: str
    from_agent: str
    to_agent: str
    content: str
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    message_type: str = "text"  # text, request, response, notification
    metadata: Dict[str, Any] = field(default_factory=dict)
    read: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "content": self.content,
            "timestamp": self.timestamp,
            "message_type": self.message_type,
            "metadata": self.metadata,
            "read": self.read,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        return cls(
            message_id=data["message_id"],
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            content=data["content"],
            timestamp=data.get("timestamp", datetime.now().timestamp()),
            message_type=data.get("message_type", "text"),
            metadata=data.get("metadata", {}),
            read=data.get("read", False),
        )


class AgentManager:
    """
    多 Agent 管理器
    
    功能:
    - Agent 注册/注销
    - Agent 状态管理
    - Agent 间通信
    - 记忆空间隔离
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = Path(memory_dir)
        self.agents_dir = self.memory_dir / "agents"
        self.messages_dir = self.memory_dir / "agent_messages"
        self.shared_spaces_dir = self.memory_dir / "shared_spaces"
        
        # 创建必要目录
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.messages_dir.mkdir(parents=True, exist_ok=True)
        self.shared_spaces_dir.mkdir(parents=True, exist_ok=True)
        
        # Agent 缓存
        self._agents: Dict[str, AgentConfig] = {}
        self._message_queues: Dict[str, List[AgentMessage]] = {}
        
        # 加载已有 Agent
        self._load_agents()
    
    def _load_agents(self):
        """加载已注册的 Agent"""
        agents_file = self.agents_dir / "agents.json"
        if agents_file.exists():
            try:
                with open(agents_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for agent_data in data:
                        self._agents[agent_data["agent_id"]] = AgentConfig.from_dict(agent_data)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_agents(self):
        """保存 Agent 列表"""
        agents_file = self.agents_dir / "agents.json"
        data = [agent.to_dict() for agent in self._agents.values()]
        with open(agents_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def register_agent(
        self,
        name: str,
        role: AgentRole = AgentRole.ASSISTANT,
        description: str = "",
        isolated_memory: bool = True,
    ) -> str:
        """
        注册新 Agent
        
        Args:
            name: Agent 名称
            role: Agent 角色
            description: 描述
            isolated_memory: 是否使用独立记忆空间
        
        Returns:
            Agent ID
        """
        agent_id = str(uuid.uuid4())
        
        config = AgentConfig(
            agent_id=agent_id,
            name=name,
            role=role,
            description=description,
            isolated_memory=isolated_memory,
        )
        
        self._agents[agent_id] = config
        self._save_agents()
        
        # 创建 Agent 专用目录
        if isolated_memory:
            agent_memory_dir = self.memory_dir / "agents" / agent_id
            agent_memory_dir.mkdir(parents=True, exist_ok=True)
        
        return agent_id
    
    def unregister_agent(self, agent_id: str) -> bool:
        """注销 Agent"""
        if agent_id not in self._agents:
            return False
        
        del self._agents[agent_id]
        self._save_agents()
        return True
    
    def get_agent(self, agent_id: str) -> Optional[AgentConfig]:
        """获取 Agent 配置"""
        return self._agents.get(agent_id)
    
    def list_agents(self, status: Optional[AgentStatus] = None) -> List[AgentConfig]:
        """列出所有 Agent"""
        agents = list(self._agents.values())
        if status:
            agents = [a for a in agents if a.status == status]
        return agents
    
    def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """更新 Agent 状态"""
        if agent_id not in self._agents:
            return False
        
        agent = self._agents[agent_id]
        agent.status = status
        agent.last_active = datetime.now().timestamp()
        self._save_agents()
        return True
    
    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        content: str,
        message_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        发送 Agent 间消息
        
        Args:
            from_agent: 发送方 Agent ID
            to_agent: 接收方 Agent ID
            content: 消息内容
            message_type: 消息类型
            metadata: 额外元数据
        
        Returns:
            消息 ID
        """
        # 检查权限
        sender = self._agents.get(from_agent)
        receiver = self._agents.get(to_agent)
        
        if not sender or not receiver:
            raise ValueError("Agent 不存在")
        
        if not sender.can_send_messages or not receiver.can_receive_messages:
            raise ValueError("通信权限不足")
        
        # 检查白名单
        if receiver.allowed_agents and from_agent not in receiver.allowed_agents:
            raise ValueError("不在接收方白名单中")
        
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            message_type=message_type,
            metadata=metadata or {},
        )
        
        # 添加到接收方消息队列
        if to_agent not in self._message_queues:
            self._message_queues[to_agent] = []
        self._message_queues[to_agent].append(message)
        
        # 持久化消息
        self._save_message(to_agent, message)
        
        return message.message_id
    
    def _save_message(self, agent_id: str, message: AgentMessage):
        """保存消息到文件"""
        message_file = self.messages_dir / f"{agent_id}.jsonl"
        with open(message_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(message.to_dict(), ensure_ascii=False) + '\n')
    
    def get_messages(self, agent_id: str, mark_as_read: bool = True) -> List[AgentMessage]:
        """获取 Agent 的消息"""
        if agent_id not in self._message_queues:
            # 从文件加载
            self._load_messages(agent_id)
        
        messages = self._message_queues.get(agent_id, [])
        
        if mark_as_read and messages:
            for msg in messages:
                msg.read = True
        
        return messages
    
    def _load_messages(self, agent_id: str):
        """从文件加载消息"""
        message_file = self.messages_dir / f"{agent_id}.jsonl"
        messages = []
        
        if message_file.exists():
            try:
                with open(message_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            messages.append(AgentMessage.from_dict(data))
            except (json.JSONDecodeError, IOError):
                pass
        
        self._message_queues[agent_id] = messages
    
    def create_shared_space(self, name: str, agents: List[str]) -> str:
        """
        创建共享记忆空间
        
        Args:
            name: 空间名称
            agents: 参与 Agent 列表
        
        Returns:
            空间 ID
        """
        space_id = str(uuid.uuid4())
        space_dir = self.shared_spaces_dir / space_id
        space_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建空间配置
        config = {
            "space_id": space_id,
            "name": name,
            "agents": agents,
            "created_at": datetime.now().timestamp(),
        }
        
        config_file = space_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # 更新 Agent 的共享空间列表
        for agent_id in agents:
            if agent_id in self._agents:
                self._agents[agent_id].shared_memory_spaces.add(space_id)
        
        self._save_agents()
        
        return space_id
    
    def get_agent_memory_path(self, agent_id: str) -> Path:
        """获取 Agent 的记忆目录路径"""
        agent = self._agents.get(agent_id)
        
        if not agent:
            raise ValueError("Agent 不存在")
        
        if agent.isolated_memory:
            return self.memory_dir / "agents" / agent_id / "memory"
        else:
            return self.memory_dir / "shared" / "memory"
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "total_agents": len(self._agents),
            "active_agents": sum(1 for a in self._agents.values() if a.status == AgentStatus.ACTIVE),
            "inactive_agents": sum(1 for a in self._agents.values() if a.status == AgentStatus.INACTIVE),
            "busy_agents": sum(1 for a in self._agents.values() if a.status == AgentStatus.BUSY),
            "roles": {},
        }
        
        # 按角色统计
        for agent in self._agents.values():
            role = agent.role.value
            stats["roles"][role] = stats["roles"].get(role, 0) + 1
        
        return stats
