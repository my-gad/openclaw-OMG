# 多 Agent 支持文档

## 🎯 功能概述

OpenClaw-OMG v1.6.0+ 提供多 Agent 协作支持，允许：
- 多个 Agent 同时运行和协作
- Agent 间消息传递
- 记忆空间隔离或共享
- 角色和权限管理

## 📋 Agent 角色

| 角色 | 说明 | 用途 |
|------|------|------|
| `main` | 主 Agent | 系统主要协调者 |
| `assistant` | 助手 Agent | 协助主 Agent 处理任务 |
| `specialist` | 专家 Agent | 提供特定领域专业知识 |
| `observer` | 观察者 | 监控和记录，不主动参与 |

## 🚀 快速开始

### 注册 Agent

```bash
# 注册主 Agent
python3 -m memory_system.cli agent-register "运维 - 汪维维" \
    --role main \
    --description "系统维护运维 Agent"

# 注册助手 Agent
python3 -m memory_system.cli agent-register "大管家 - 汪小白" \
    --role assistant \
    --description "家族事务管理 Agent"

# 注册专家 Agent
python3 -m memory_system.cli agent-register "技术专家" \
    --role specialist \
    --description "技术咨询专家"
```

### 查看 Agent 列表

```bash
python3 -m memory_system.cli agent-list
```

### 查看 Agent 系统状态

```bash
python3 -m memory_system.cli agent-status
```

## 💡 Python API 使用

### 注册 Agent

```python
from pathlib import Path
from memory_system.multiagent import AgentManager, AgentRole

# 初始化 Agent 管理器
manager = AgentManager(Path('./memory'))

# 注册 Agent
agent_id = manager.register_agent(
    name="运维 - 汪维维",
    role=AgentRole.MAIN,
    description="系统维护运维 Agent",
    isolated_memory=True  # 使用独立记忆空间
)
print(f"Agent ID: {agent_id}")
```

### Agent 间通信

```python
# 注册两个 Agent
agent1_id = manager.register_agent("Agent 1")
agent2_id = manager.register_agent("Agent 2")

# 发送消息
message_id = manager.send_message(
    from_agent=agent1_id,
    to_agent=agent2_id,
    content="请处理这个任务",
    message_type="request",  # text, request, response, notification
    metadata={"priority": "high"}
)

# 接收消息
messages = manager.get_messages(agent2_id, mark_as_read=True)
for msg in messages:
    print(f"来自 {msg.from_agent}: {msg.content}")
```

### 创建共享记忆空间

```python
# 创建共享空间
space_id = manager.create_shared_space(
    name="项目协作空间",
    agents=[agent1_id, agent2_id]
)

# Agent 可以访问共享空间中的记忆
agent1_memory_path = manager.get_agent_memory_path(agent1_id)
agent2_memory_path = manager.get_agent_memory_path(agent2_id)
```

### 更新 Agent 状态

```python
# 设置为活跃
manager.update_agent_status(agent_id, AgentStatus.ACTIVE)

# 设置为忙碌
manager.update_agent_status(agent_id, AgentStatus.BUSY)

# 设置为非活跃
manager.update_agent_status(agent_id, AgentStatus.INACTIVE)
```

## 📊 CLI 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `agent-register` | 注册新 Agent | `agent-register "名称" --role main` |
| `agent-list` | 列出所有 Agent | `agent-list` |
| `agent-status` | 查看系统状态 | `agent-status` |

### agent-register 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `name` | Agent 名称 | 必需 |
| `--role` | 角色 (main/assistant/specialist/observer) | assistant |
| `--description` | 描述 | 空 |
| `--shared-memory` | 使用共享记忆空间 | False |

## 🔧 配置选项

### Agent 配置

```python
from memory_system.multiagent import AgentConfig

config = AgentConfig(
    agent_id="agent-123",
    name="Agent 名称",
    role=AgentRole.MAIN,
    description="描述",
    isolated_memory=True,  # 记忆隔离
    can_send_messages=True,  # 可发送消息
    can_receive_messages=True,  # 可接收消息
    allowed_agents=set(),  # 白名单（空表示无限制）
)
```

### 消息类型

| 类型 | 说明 | 用途 |
|------|------|------|
| `text` | 普通文本消息 | 一般交流 |
| `request` | 请求消息 | 请求帮助或信息 |
| `response` | 响应消息 | 回复请求 |
| `notification` | 通知消息 | 系统通知或提醒 |

## 📁 目录结构

```
memory/
├── agents/                 # Agent 目录
│   ├── agents.json        # Agent 注册信息
│   ├── {agent_id}/        # Agent 独立记忆空间
│   │   └── memory/
├── agent_messages/         # Agent 间消息
│   ├── {agent_id}.jsonl   # 每个 Agent 的消息队列
├── shared_spaces/          # 共享记忆空间
│   ├── {space_id}/
│   │   ├── config.json    # 空间配置
│   │   └── memory/        # 共享记忆
```

## 🔐 安全和权限

### 消息权限

- `can_send_messages`: 控制是否可以发送消息
- `can_receive_messages`: 控制是否可以接收消息
- `allowed_agents`: 白名单，只有列表中的 Agent 可以发送消息

### 记忆隔离

- `isolated_memory=True`: 每个 Agent 有独立的记忆空间
- `isolated_memory=False`: 所有 Agent 共享同一记忆空间
- 共享空间需要显式创建并添加参与 Agent

## 📊 统计信息

```python
stats = manager.get_stats()
print(stats)
# {
#     "total_agents": 3,
#     "active_agents": 1,
#     "inactive_agents": 2,
#     "busy_agents": 0,
#     "roles": {
#         "main": 1,
#         "assistant": 2
#     }
# }
```

## 🎯 使用场景

### 场景 1: 多 Agent 协作

```python
# 注册主 Agent 和助手 Agent
main_id = manager.register_agent("主 Agent", role=AgentRole.MAIN)
assistant_id = manager.register_agent("助手 Agent", role=AgentRole.ASSISTANT)

# 主 Agent 发送任务
manager.send_message(
    from_agent=main_id,
    to_agent=assistant_id,
    content="请查询今天的天气",
    message_type="request"
)

# 助手 Agent 处理并回复
manager.send_message(
    from_agent=assistant_id,
    to_agent=main_id,
    content="今天天气晴朗，温度 25°C",
    message_type="response"
)
```

### 场景 2: 专家咨询

```python
# 注册专家 Agent
expert_id = manager.register_agent("法律专家", role=AgentRole.SPECIALIST)

# 创建共享空间供咨询使用
space_id = manager.create_shared_space(
    name="法律咨询空间",
    agents=[main_id, expert_id]
)

# 在共享空间中共享相关法律文档
# ...
```

## ✅ 测试

运行多 Agent 测试：

```bash
python3 -m unittest tests.test_multiagent -v
```

测试覆盖：
- Agent 注册/注销
- Agent 状态管理
- 消息发送/接收
- 共享空间创建
- 记忆隔离

## 🔗 相关文档

- [README.md](README.md) - 项目主文档
- [API 参考](docs/API.md) - 完整 API 文档
- [示例代码](examples/multiagent/) - 使用示例

---

**版本:** v1.6.0+  
**最后更新:** 2026-03-09
