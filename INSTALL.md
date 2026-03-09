# OpenClaw-OMG 安装与配置指南

## 📋 目录

- [快速开始](#快速开始)
- [详细安装步骤](#详细安装步骤)
- [配置说明](#配置说明)
- [多 Agent 配置](#多-agent-配置)
- [常见问题](#常见问题)
- [升级指南](#升级指南)

---

## 🚀 快速开始

### 1. 克隆项目

```bash
cd /home/administrator/.openclaw/workspace
git clone https://github.com/my-gad/openclaw-OMG.git
cd openclaw-OMG
```

### 2. 初始化记忆系统

```bash
export PYTHONPATH=/home/administrator/.openclaw/workspace/openclaw-OMG/src:$PYTHONPATH
python3 -m memory_system.cli init
```

### 3. 验证安装

```bash
python3 -m memory_system.cli status
```

### 4. 注册 Agent（可选）

```bash
# 注册主 Agent
python3 -m memory_system.cli agent-register "主 Agent" --role main

# 查看 Agent 列表
python3 -m memory_system.cli agent-list
```

完成！现在可以开始使用记忆系统了。

---

## 📦 详细安装步骤

### 系统要求

- Python 3.8+
- SQLite 3+
- 内存：至少 256MB 可用空间
- 存储：至少 100MB 可用空间

### 步骤 1: 安装依赖

```bash
# 进入项目目录
cd /home/administrator/.openclaw/workspace/openclaw-OMG

# 安装 Python 依赖（如果有 requirements.txt）
pip install -r requirements.txt

# 或者只安装必要的依赖
pip install sqlite3  # 通常已包含在 Python 中
```

### 步骤 2: 设置环境变量

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export PYTHONPATH=/home/administrator/.openclaw/workspace/openclaw-OMG/src:$PYTHONPATH

# 或者临时设置
export PYTHONPATH=/home/administrator/.openclaw/workspace/openclaw-OMG/src
```

### 步骤 3: 创建必要目录

```bash
# 项目会自动创建，但手动创建也可以
mkdir -p /home/administrator/.openclaw/workspace/openclaw-OMG/memory
```

### 步骤 4: 初始化记忆系统

```bash
cd /home/administrator/.openclaw/workspace/openclaw-OMG
python3 -m memory_system.cli init
```

输出示例：
```
🧠 初始化 Memory System v1.6.0
创建目录结构:
  - memory/layer1 (工作记忆)
  - memory/layer2/active (活跃记忆)
  - memory/layer2/archive (归档记忆)
  - memory/layer2/entities (实体)
  - memory/layer3 (原始事件)
  - memory/agents (Agent 目录)
  - memory/shared_spaces (共享空间)
✅ 初始化完成
```

### 步骤 5: 验证安装

```bash
# 查看系统状态
python3 -m memory_system.cli status

# 运行测试
python3 -m unittest discover tests -v
```

---

## ⚙️ 配置说明

### 配置文件位置

配置文件位于 `memory/config.json`

### 配置示例

```json
{
  "version": "1.6.0",
  "memory_dir": "./memory",
  
  "decay_rates": {
    "fact": 0.008,
    "belief": 0.07,
    "summary": 0.025
  },
  
  "thresholds": {
    "archive": 0.3,
    "delete": 0.1
  },
  
  "llm": {
    "enabled": true,
    "min_confidence": 0.6,
    "api_key_source": "env",
    "max_retries": 3
  },
  
  "entity_system": {
    "enabled": true,
    "learn_new_entities": true,
    "max_learned_entities": 1000
  },
  
  "multiagent": {
    "enabled": true,
    "default_isolation": true
  }
}
```

### 配置项说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `version` | 配置版本 | "1.6.0" |
| `memory_dir` | 记忆存储目录 | "./memory" |
| `decay_rates.fact` | 事实记忆衰减率 | 0.008 |
| `decay_rates.belief` | 信念记忆衰减率 | 0.07 |
| `thresholds.archive` | 归档阈值 | 0.3 |
| `thresholds.delete` | 删除阈值 | 0.1 |
| `llm.enabled` | 是否启用 LLM | true |
| `llm.min_confidence` | LLM 触发置信度 | 0.6 |
| `entity_system.enabled` | 是否启用实体系统 | true |
| `multiagent.enabled` | 是否启用多 Agent | true |

---

## 👥 多 Agent 配置

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

### Agent 角色说明

| 角色 | 说明 | 适用场景 |
|------|------|----------|
| `main` | 主 Agent | 系统协调者，决策者 |
| `assistant` | 助手 Agent | 协助主 Agent，处理日常任务 |
| `specialist` | 专家 Agent | 提供专业领域知识 |
| `observer` | 观察者 | 监控和记录，不主动参与 |

### Agent 间通信

```bash
# 查看 Agent 列表
python3 -m memory_system.cli agent-list

# 查看 Agent 系统状态
python3 -m memory_system.cli agent-status
```

### Python API 使用

```python
from pathlib import Path
from memory_system.multiagent import AgentManager, AgentRole

# 初始化 Agent 管理器
manager = AgentManager(Path('./memory'))

# 注册 Agent
agent_id = manager.register_agent(
    name="我的 Agent",
    role=AgentRole.ASSISTANT,
    description="描述",
    isolated_memory=True
)

# 发送消息
manager.send_message(
    from_agent="agent1_id",
    to_agent="agent2_id",
    content="消息内容",
    message_type="text"
)

# 接收消息
messages = manager.get_messages("agent_id")
for msg in messages:
    print(f"{msg.from_agent}: {msg.content}")
```

---

## 🔧 常见问题

### 1. 导入错误

**问题**: `ImportError: cannot import name 'MemoryManager'`

**解决**:
```bash
# 确保设置了正确的 PYTHONPATH
export PYTHONPATH=/home/administrator/.openclaw/workspace/openclaw-OMG/src:$PYTHONPATH

# 或者使用绝对路径导入
python3 -c "import sys; sys.path.insert(0, '/path/to/src'); from memory_system import ..."
```

### 2. SQLite 数据库锁定

**问题**: `sqlite3.OperationalError: database is locked`

**解决**:
```bash
# 关闭所有使用该数据库的程序
# 或者删除锁文件
rm memory/layer2/memories.db-shm
rm memory/layer2/memories.db-wal

# 如果问题持续，重新初始化
python3 -m memory_system.cli cleanup
```

### 3. 多 Agent 模块不可用

**问题**: `❌ 多 Agent 模块不可用`

**解决**:
```bash
# 检查模块是否存在
ls src/memory_system/multiagent/

# 重新安装依赖
pip install -r requirements.txt

# 检查 Python 路径
python3 -c "import sys; print('\\n'.join(sys.path))"
```

### 4. 记忆目录权限问题

**问题**: `PermissionError: [Errno 13] Permission denied`

**解决**:
```bash
# 修改目录权限
chmod -R 755 memory/

# 或者修改所有者
chown -R $USER:$USER memory/
```

### 5. 测试失败

**问题**: 部分测试用例失败

**解决**:
```bash
# 清理测试缓存
rm -rf tests/__pycache__
rm -rf src/memory_system/__pycache__

# 重新运行测试
PYTHONPATH=src python3 -m unittest discover tests -v

# 如果问题持续，检查具体测试日志
```

---

## 📈 升级指南

### 从 v1.5.0 升级到 v1.6.0

```bash
# 1. 备份现有数据
cp -r memory memory_backup_$(date +%Y%m%d)

# 2. 拉取最新代码
git pull origin main

# 3. 安装新依赖
pip install -r requirements.txt

# 4. 运行迁移脚本（如果有）
python3 scripts/migrate_v1.5_to_v1.6.py

# 5. 验证升级
python3 -m memory_system.cli status
python3 -m memory_system.cli agent-status
```

### 从 v1.4.0 或更早版本升级

```bash
# 1. 备份数据
cp -r memory memory_backup

# 2. 导出所有记忆
python3 -m memory_system.cli export -o backup.json

# 3. 重新初始化
rm -rf memory/
python3 -m memory_system.cli init

# 4. 导入数据
python3 -m memory_system.cli import backup.json

# 5. 验证
python3 -m memory_system.cli status
```

---

## 🧪 测试

### 运行所有测试

```bash
cd /home/administrator/.openclaw/workspace/openclaw-OMG
export PYTHONPATH=/home/administrator/.openclaw/workspace/openclaw-OMG/src:$PYTHONPATH

python3 -m unittest discover tests -v
```

### 运行特定测试

```bash
# MemoryManager 测试
python3 -m unittest tests.test_memory_manager -v

# EntitySystem 测试
python3 -m unittest tests.test_entity_system -v

# MultiAgent 测试
python3 -m unittest tests.test_multiagent -v
```

### 测试覆盖率

```bash
# 安装 coverage 工具
pip install coverage

# 运行测试并生成报告
coverage run -m unittest discover tests
coverage report
coverage html  # 生成 HTML 报告
```

---

## 📚 使用示例

### 基本使用

```bash
# 添加记忆
python3 -m memory_system.cli add "OpenClaw-OMG 是一个记忆超系统" \
    --type fact \
    --confidence 0.9 \
    --tags "AI,记忆"

# 搜索记忆
python3 -m memory_system.cli search "记忆"

# 查看状态
python3 -m memory_system.cli status

# 导出记忆
python3 -m memory_system.cli export -o backup.json

# 导入记忆
python3 -m memory_system.cli import backup.json
```

### 多 Agent 使用

```bash
# 注册 Agent
python3 -m memory_system.cli agent-register "助手" --role assistant

# 查看 Agent 列表
python3 -m memory_system.cli agent-list

# 查看系统状态
python3 -m memory_system.cli agent-status
```

---

## 🔗 相关文档

- [README.md](README.md) - 项目主文档
- [MULTIAGENT.md](MULTIAGENT.md) - 多 Agent 文档
- [CODE_COMPARISON.md](CODE_COMPARISON.md) - 代码对比
- [FINAL_SUMMARY.md](FINAL_SUMMARY.md) - 完成总结

---

## 🆘 获取帮助

如果遇到问题：

1. 查看 [常见问题](#常见问题)
2. 检查日志文件：`memory/*.log`
3. 运行诊断命令：`python3 -m memory_system.cli status`
4. 提交 Issue: https://github.com/my-gad/openclaw-OMG/issues

---

**版本**: v1.6.0  
**最后更新**: 2026-03-09  
**维护者**: 运维 - 汪维维 (main)
