# 多助手配置指南

## 🎯 为什么不用环境变量？

**问题：** 如果有多个助手同时运行，使用环境变量会导致：

1. **配置冲突**：后启动的助手会覆盖先启动的配置
2. **身份混淆**：无法区分不同助手的身份
3. **无法并行**：无法同时运行多个不同的助手

**解决方案：** 每个助手使用**独立的配置文件**，互不干扰。

---

## 📋 配置文件方式

### 方案 1: 独立配置文件（推荐）

每个助手有自己的配置目录和配置文件：

```
openclaw-OMG/
├── assistants/
│   ├── assistant_a/           # 助手 A
│   │   └── config.json        # 配置文件
│   └── assistant_b/           # 助手 B
│       └── config.json        # 配置文件
├── run_assistant_a.py         # 助手 A 启动脚本
└── run_assistant_b.py         # 助手 B 启动脚本
```

### 配置文件示例

**助手 A 配置** (`assistants/assistant_a/config.json`):
```json
{
  "agent_name": "运维助手",
  "agent_role": "assistant",
  "agent_description": "负责系统运维的助手",
  "default_org": "运维团队",
  "memory_dir": "./memory",
  "isolated_memory": true
}
```

**助手 B 配置** (`assistants/assistant_b/config.json`):
```json
{
  "agent_name": "客服助手",
  "agent_role": "assistant",
  "agent_description": "负责客户服务的助手",
  "default_org": "客服团队",
  "memory_dir": "./memory",
  "isolated_memory": true
}
```

---

## 🚀 启动方式

### 方式 1: 使用启动脚本（推荐）

创建启动脚本 `run_assistant_a.py`:

```python
#!/usr/bin/env python3
"""运维助手启动脚本"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from memory_system.multiagent.agent_config import auto_register_with_config

print("🚀 启动运维助手...")
result = auto_register_with_config(
    config_path=Path("assistants/assistant_a/config.json")
)

if result["success"]:
    print(f"✅ Agent 已就绪")
    print(f"   ID: {result['agent_id']}")
else:
    print(f"❌ 启动失败：{result['message']}")
    sys.exit(1)

# ... 助手的业务逻辑
```

**同时运行多个助手：**

```bash
# 终端 1 - 启动运维助手
python3 run_assistant_a.py

# 终端 2 - 启动客服助手
python3 run_assistant_b.py

# 两个助手同时运行，互不干扰！
```

### 方式 2: 命令行指定配置

```bash
# 启动助手 A
python3 -m memory_system.multiagent.agent_config \
    --config assistants/assistant_a/config.json \
    --name "运维助手" \
    --org "运维团队"

# 启动助手 B
python3 -m memory_system.multiagent.agent_config \
    --config assistants/assistant_b/config.json \
    --name "客服助手" \
    --org "客服团队"
```

### 方式 3: 代码内直接指定

```python
from memory_system.multiagent.agent_config import auto_register_with_config
from pathlib import Path

# 助手 A
result_a = auto_register_with_config(
    config_path=Path("assistants/assistant_a/config.json")
)

# 助手 B
result_b = auto_register_with_config(
    config_path=Path("assistants/assistant_b/config.json")
)
```

---

## 📁 配置文件说明

### 配置项

| 配置项 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `agent_name` | Agent 名称 | 无 | ✅ |
| `agent_role` | Agent 角色 | `assistant` | ❌ |
| `agent_description` | Agent 描述 | 自动生成 | ❌ |
| `default_org` | 默认组织名称 | 无 | ❌ |
| `parent_org` | 父组织名称 | 无 | ❌ |
| `memory_dir` | 记忆目录 | `./memory` | ❌ |
| `isolated_memory` | 是否隔离记忆 | `true` | ❌ |

### 配置示例

**基础配置：**
```json
{
  "agent_name": "我的助手"
}
```

**完整配置：**
```json
{
  "agent_name": "运维助手",
  "agent_role": "assistant",
  "agent_description": "负责系统运维的助手",
  "default_org": "运维团队",
  "parent_org": "技术部",
  "memory_dir": "./memory",
  "isolated_memory": true
}
```

---

## 🎯 多助手场景

### 场景 1: 部门协作

```
公司总部 (根组织)
├── 技术部
│   ├── 运维助手 (assistant_a)
│   └── 开发助手 (assistant_c)
└── 客服部
    └── 客服助手 (assistant_b)
```

**配置文件：**

- `assistants/assistant_a/config.json` - 运维助手
- `assistants/assistant_b/config.json` - 客服助手
- `assistants/assistant_c/config.json` - 开发助手

**同时运行：**

```bash
# 三个终端同时运行
python3 run_assistant_a.py  # 运维助手
python3 run_assistant_b.py  # 客服助手
python3 run_assistant_c.py  # 开发助手
```

### 场景 2: 多租户环境

```
租户 A
├── 助手 A1
└── 助手 A2

租户 B
├── 助手 B1
└── 助手 B2
```

每个租户有独立的配置目录：

```
assistants/
├── tenant_a/
│   ├── assistant_1/
│   └── assistant_2/
└── tenant_b/
    ├── assistant_1/
    └── assistant_2/
```

---

## ✅ 最佳实践

### 1. 为每个助手创建独立目录

```bash
# 创建助手目录
mkdir -p assistants/my_assistant

# 创建配置文件
cat > assistants/my_assistant/config.json << 'EOF'
{
  "agent_name": "我的助手",
  "agent_role": "assistant",
  "default_org": "我的团队"
}
EOF
```

### 2. 使用有意义的命名

```
assistants/
├── yunwei_assistant/    # 运维助手
├── kefu_assistant/      # 客服助手
├── xiaoshou_assistant/  # 销售助手
└── renshi_assistant/    # 人事助手
```

### 3. 版本控制

```bash
# 将配置文件纳入版本控制
git add assistants/*/config.json

# 但忽略运行数据
echo "memory/" >> .gitignore
echo "*.pyc" >> .gitignore
```

### 4. 环境区分

```
assistants/
├── dev/           # 开发环境
│   └── config.json
├── test/          # 测试环境
│   └── config.json
└── prod/          # 生产环境
    └── config.json
```

---

## 🔧 配置管理

### 查看当前配置

```bash
python3 -m memory_system.multiagent.agent_config \
    --config assistants/assistant_a/config.json \
    --show
```

### 更新配置

```bash
# 更新 Agent 名称
python3 -m memory_system.multiagent.agent_config \
    --config assistants/assistant_a/config.json \
    --name "新的助手名称"

# 更新默认组织
python3 -m memory_system.multiagent.agent_config \
    --config assistants/assistant_a/config.json \
    --org "新的团队"
```

### 验证配置

```python
from memory_system.multiagent.agent_config import AgentConfigManager
from pathlib import Path

manager = AgentConfigManager(Path("assistants/assistant_a/config.json"))
config = manager.config

print(f"Agent 名称：{config.agent_name}")
print(f"默认组织：{config.default_org}")
print(f"记忆隔离：{config.isolated_memory}")
```

---

## 📊 对比

| 特性 | 环境变量方式 | 配置文件方式 |
|------|------------|------------|
| 多助手并行 | ❌ 冲突 | ✅ 支持 |
| 配置隔离 | ❌ 共享 | ✅ 独立 |
| 版本控制 | ❌ 困难 | ✅ 容易 |
| 环境区分 | ❌ 困难 | ✅ 容易 |
| 配置管理 | ❌ 分散 | ✅ 集中 |
| 推荐使用 | ❌ 不推荐 | ✅ 推荐 |

---

## 🔗 相关文档

- [AUTO_REGISTER_GUIDE.md](AUTO_REGISTER_GUIDE.md) - 自动注册
- [ORGANIZATION_GUIDE.md](ORGANIZATION_GUIDE.md) - 组织架构
- [MULTIAGENT.md](MULTIAGENT.md) - 多 Agent 支持

---

**版本**: v1.6.0+  
**最后更新**: 2026-03-09  
**维护者**: 运维 - 汪维维 (main)
