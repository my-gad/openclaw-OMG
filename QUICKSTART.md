# OpenClaw-OMG 快速开始指南

## 🚀 30 秒快速开始

```bash
# 1. 进入项目目录
cd /home/administrator/.openclaw/workspace/openclaw-OMG

# 2. 初始化
export PYTHONPATH=/home/administrator/.openclaw/workspace/openclaw-OMG/src:$PYTHONPATH
python3 -m memory_system.cli init

# 3. 完成！
python3 -m memory_system.cli status
```

---

## 📋 常用命令

### 记忆管理

```bash
# 添加记忆
python3 -m memory_system.cli add "这是事实" --type fact --confidence 0.9

# 搜索记忆
python3 -m memory_system.cli search "关键词"

# 列出所有记忆
python3 -m memory_system.cli list

# 查看状态
python3 -m memory_system.cli status
```

### 多 Agent

```bash
# 注册 Agent
python3 -m memory_system.cli agent-register "我的 Agent" --role main

# 查看 Agent 列表
python3 -m memory_system.cli agent-list

# 查看系统状态
python3 -m memory_system.cli agent-status
```

### 数据管理

```bash
# 导出
python3 -m memory_system.cli export -o backup.json

# 导入
python3 -m memory_system.cli import backup.json

# 清理
python3 -m memory_system.cli cleanup
```

---

## 📚 完整文档

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 项目介绍 |
| [INSTALL.md](INSTALL.md) | 详细安装指南 |
| [SKILL_GUIDE.md](SKILL_GUIDE.md) | Skill 开发指南 |
| [MULTIAGENT.md](MULTIAGENT.md) | 多 Agent 文档 |
| [CODE_COMPARISON.md](CODE_COMPARISON.md) | 代码对比 |
| [FINAL_SUMMARY.md](FINAL_SUMMARY.md) | 完成总结 |

---

## 🎯 Python 使用示例

```python
from pathlib import Path
from memory_system.core import MemoryManager, MemoryType
from memory_system.multiagent import AgentManager, AgentRole

# 初始化记忆管理器
manager = MemoryManager(Path('./memory'))

# 添加记忆
record_id = manager.add(
    content="OpenClaw-OMG 是记忆超系统",
    memory_type=MemoryType.FACT,
    confidence=0.9,
    tags=["AI", "记忆"]
)

# 搜索记忆
results = manager.search("记忆")
for r in results:
    print(f"{r.content} (置信度：{r.confidence})")

# 多 Agent 支持
agent_manager = AgentManager(Path('./memory'))
agent_id = agent_manager.register_agent(
    name="助手",
    role=AgentRole.ASSISTANT
)

# Agent 间通信
agent_manager.send_message(
    from_agent=agent_id,
    to_agent="other_agent_id",
    content="协作消息"
)
```

---

## 🔧 快速配置

### 环境变量

```bash
# 添加到 ~/.bashrc
export PYTHONPATH=/home/administrator/.openclaw/workspace/openclaw-OMG/src:$PYTHONPATH
```

### 配置文件

编辑 `memory/config.json`：

```json
{
  "version": "1.6.0",
  "memory_dir": "./memory",
  "llm": {
    "enabled": true,
    "min_confidence": 0.6
  }
}
```

---

## ❓ 常见问题

**Q: 导入错误怎么办？**  
A: 确保设置了正确的 PYTHONPATH

**Q: 如何备份数据？**  
A: 使用 `python3 -m memory_system.cli export -o backup.json`

**Q: 多 Agent 如何使用？**  
A: 参考 [MULTIAGENT.md](MULTIAGENT.md)

**Q: 如何升级？**  
A: 参考 [INSTALL.md](INSTALL.md) 的升级指南

---

## 🆘 获取帮助

1. 查看文档：`ls *.md`
2. 运行测试：`python3 -m unittest discover tests -v`
3. 提交 Issue: https://github.com/ktao732084-arch/openclaw-OMG/issues

---

**版本**: v1.6.0  
**更新时间**: 2026-03-09
