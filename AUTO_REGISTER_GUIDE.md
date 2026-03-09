# 自动注册指南

## 🎯 功能概述

OpenClaw-OMG v1.6.0+ 提供**自动注册机制**：

- ✅ **首次运行自动注册**：Agent 首次启动时自动完成注册
- ✅ **重复运行不重复注册**：智能检测，避免重复
- ✅ **自动加入组织**：可配置默认组织，自动加入
- ✅ **环境变量配置**：支持通过环境变量灵活配置
- ✅ **一键启动**：在助手启动脚本中调用即可

---

## 🚀 快速开始

### 方式 1: 在 Python 代码中自动注册

```python
from memory_system.multiagent.auto_register import quick_start

# 最简单的方式 - 自动从环境变量读取
result = quick_start()

print(f"Agent ID: {result['agent_id']}")
print(f"是否新注册：{result['is_new']}")
```

### 方式 2: 指定参数

```python
from memory_system.multiagent.auto_register import quick_setup
from pathlib import Path

result = quick_setup(
    agent_name="我的助手",  # 可选，默认从环境变量获取
    org_name="我的团队",    # 可选，自动加入组织
    memory_dir=Path("./memory"),
)

print(f"Agent ID: {result['agent_id']}")
print(f"组织 ID: {result['org_id']}")
```

### 方式 3: 命令行调用

```bash
# 自动注册当前 Agent
python3 -m memory_system.multiagent.auto_register \
    --name "我的助手" \
    --org "我的团队"

# 或在启动脚本中调用
python3 -m memory_system.auto_start --dir ./memory
```

---

## 📋 环境变量

### 配置变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENCLAW_AGENT_NAME` | Agent 名称 | `{user}@{host}` |
| `OPENCLAW_AGENT_ROLE` | Agent 角色 | `assistant` |
| `OPENCLAW_AGENT_DESCRIPTION` | Agent 描述 | 自动生成 |
| `OPENCLAW_DEFAULT_ORG` | 默认组织名称 | 空 |
| `OPENCLAW_AUTO_JOIN` | 是否自动加入组织 | `true` |
| `OPENCLAW_MEMORY_DIR` | 记忆目录 | `./memory` |

### 设置示例

```bash
# 在 ~/.bashrc 或启动脚本中设置
export OPENCLAW_AGENT_NAME="运维助手"
export OPENCLAW_AGENT_ROLE="assistant"
export OPENCLAW_DEFAULT_ORG="运维团队"
export OPENCLAW_MEMORY_DIR="/path/to/memory"

# 启动助手
python3 my_assistant.py
```

---

## 💻 使用场景

### 场景 1: 助手启动时自动注册

在助手的启动脚本中：

```python
#!/usr/bin/env python3
"""
助手启动脚本
"""

import os
os.environ["OPENCLAW_AGENT_NAME"] = "我的助手"
os.environ["OPENCLAW_DEFAULT_ORG"] = "助手团队"

# 自动注册
from memory_system.multiagent.auto_register import quick_start
result = quick_start()

if result["success"]:
    print(f"✓ Agent 已就绪：{result['agent_id']}")
else:
    print(f"⚠️ 注册失败：{result['message']}")

# ... 继续助手的其他逻辑
```

### 场景 2: 多助手协作环境

```python
# 助手 A - 运维助手
os.environ["OPENCLAW_AGENT_NAME"] = "运维助手"
os.environ["OPENCLAW_DEFAULT_ORG"] = "运维团队"
result_a = quick_start()

# 助手 B - 客服助手
os.environ["OPENCLAW_AGENT_NAME"] = "客服助手"
os.environ["OPENCLAW_DEFAULT_ORG"] = "客服团队"
result_b = quick_start()
```

### 场景 3: 临时助手（用完即走）

```python
import os
from memory_system.multiagent.auto_register import quick_start

# 设置临时名称
os.environ["OPENCLAW_AGENT_NAME"] = "临时助手-" + datetime.now().strftime("%Y%m%d%H%M%S")

# 自动注册，用完不保留
result = quick_start()
print(f"临时 Agent: {result['agent_id']}")

# ... 执行任务

# 任务完成后可选清理
# agent_manager.unregister_agent(result['agent_id'])
```

---

## 🔧 高级用法

### 1. 确保在组织中

```python
from memory_system.multiagent.auto_register import ensure_agent_in_org
from pathlib import Path

# 确保 Agent 在指定组织中，如果组织不存在则创建
success = ensure_agent_in_org(
    agent_id="agent-123",
    org_name="我的团队",
    memory_dir=Path("./memory"),
    create_if_missing=True,
    parent_org="父组织 ID",  # 可选
)
```

### 2. 获取当前 Agent 身份

```python
from memory_system.multiagent.auto_register import get_current_agent_identity

name, role, desc = get_current_agent_identity()
print(f"当前 Agent: {name} ({role}) - {desc}")
```

### 3. 自定义注册逻辑

```python
from memory_system.multiagent import AgentManager, AgentRole
from pathlib import Path

manager = AgentManager(Path("./memory"))

# 查找同名 Agent
existing = None
for agent in manager.list_agents():
    if agent.name == "我的助手":
        existing = agent
        break

if existing:
    # 已存在，更新状态
    manager.update_agent_status(existing.agent_id, AgentStatus.ACTIVE)
    agent_id = existing.agent_id
else:
    # 不存在，注册新的
    agent_id = manager.register_agent(
        name="我的助手",
        role=AgentRole.ASSISTANT,
        description="自定义描述",
    )
```

---

## 📊 工作流程

### 首次启动流程

```
启动助手
    ↓
调用 quick_start()
    ↓
检测环境变量
    ↓
查找是否已注册
    ↓
未找到 → 注册新 Agent
    ↓
检查默认组织
    ↓
加入/创建组织
    ↓
返回 Agent ID
```

### 重复启动流程

```
启动助手
    ↓
调用 quick_start()
    ↓
检测环境变量
    ↓
查找是否已注册
    ↓
已找到 → 更新状态为活跃
    ↓
检查组织成员资格
    ↓
返回现有 Agent ID
```

---

## 🎯 完整示例

### 示例 1: 完整的助手启动脚本

```python
#!/usr/bin/env python3
"""
助手启动脚本 - 完整示例
"""

import os
import sys
from pathlib import Path

# 配置环境变量
os.environ["OPENCLAW_AGENT_NAME"] = "我的智能助手"
os.environ["OPENCLAW_AGENT_ROLE"] = "assistant"
os.environ["OPENCLAW_DEFAULT_ORG"] = "智能助手团队"
os.environ["OPENCLAW_MEMORY_DIR"] = "./memory"

# 自动注册
from memory_system.multiagent.auto_register import quick_start

print("🚀 启动助手中...")
result = quick_start()

if not result["success"]:
    print(f"❌ 启动失败：{result['message']}")
    sys.exit(1)

print(f"✅ Agent 已就绪")
print(f"   ID: {result['agent_id']}")
print(f"   组织：{result.get('org_id', '无')}")

# ... 继续助手的其他逻辑
```

### 示例 2: 多助手协作

```python
#!/usr/bin/env python3
"""
多助手协作示例
"""

from memory_system.multiagent.auto_register import quick_setup
from memory_system.multiagent import AgentManager
from pathlib import Path

memory_dir = Path("./memory")

# 助手 1 注册
result1 = quick_setup(
    agent_name="助手 A",
    org_name="协作团队",
    memory_dir=memory_dir,
)

# 助手 2 注册
result2 = quick_setup(
    agent_name="助手 B",
    org_name="协作团队",
    memory_dir=memory_dir,
)

# 现在两个助手在同一个团队中，可以协作了
print(f"助手 A: {result1['agent_id']}")
print(f"助手 B: {result2['agent_id']}")
print(f"共同组织：{result1['org_id']}")
```

---

## ✅ 最佳实践

### 1. 在配置文件中集中管理

```python
# config.py
AGENT_CONFIG = {
    "name": "我的助手",
    "role": "assistant",
    "org": "我的团队",
    "memory_dir": "./memory",
}
```

### 2. 使用环境变量覆盖

```bash
# 开发环境
export OPENCLAW_AGENT_NAME="开发助手"
export OPENCLAW_DEFAULT_ORG="开发团队"

# 生产环境
export OPENCLAW_AGENT_NAME="生产助手"
export OPENCLAW_DEFAULT_ORG="生产团队"
```

### 3. 日志记录

```python
import logging

result = quick_start()
if result["success"]:
    logging.info(f"Agent 注册成功：{result['agent_id']}")
else:
    logging.error(f"Agent 注册失败：{result['message']}")
```

---

## 🔗 相关文档

- [ORGANIZATION_GUIDE.md](ORGANIZATION_GUIDE.md) - 组织架构
- [MULTIAGENT.md](MULTIAGENT.md) - 多 Agent 支持
- [INSTALL.md](INSTALL.md) - 安装指南

---

**版本**: v1.6.0+  
**最后更新**: 2026-03-09  
**维护者**: 运维 - 汪维维 (main)
