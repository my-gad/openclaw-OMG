---
name: openclaw-omg
version: 2.0.0
description: "OpenClaw-OMG (Optimized Memory Gateway) v2.0 - 三层记忆架构系统。即时捕获、自动评分、关键词触发、快照注入、OpenClaw 深度集成。"
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      bins: ["python3", "jq"]
    install:
      - id: "init"
        kind: "script"
        command: "cd ~/.openclaw/skills/openclaw-omg && PYTHONPATH=src python3 -m memory_system.cli init"
        label: "初始化 OMG 记忆系统"
      - id: "cron"
        kind: "script"
        command: "cd ~/.openclaw/skills/openclaw-omg && PYTHONPATH=src python3 -m memory_system.cli integration --install-cron"
        label: "安装 Cron 定时任务"
        run_on: "startup"
        condition: "cron_not_exists"
---

# OpenClaw-OMG 🧠 v2.0.0

## 安装说明

### 自动安装（推荐）

Skill 安装后自动执行：
1. 初始化记忆系统目录结构
2. **自动安装 Cron 定时任务**
3. 创建初始快照

```bash
# 查看 Skill 状态
openclaw skills list | grep omg
openclaw skills info openclaw-omg
```

### 手动安装

```bash
# 1. 克隆项目到 Skill 目录
git clone https://github.com/my-gad/openclaw-omg.git ~/.openclaw/skills/openclaw-omg

# 2. 初始化（自动安装 Cron）
cd ~/.openclaw/skills/openclaw-omg
PYTHONPATH=src python3 -m memory_system.cli init
```

---

## 核心功能

- **三层记忆架构**：工作记忆 → 长期记忆 → 原始日志
- **即时记忆捕获**：自动评分重要性，关键词触发检测
- **自动整合**：每日 Consolidation（7 阶段流程）
- **智能衰减**：基于遗忘曲线的自动衰减
- **多 Agent 支持**：组织架构、记忆共享
- **OpenClaw 集成**：快照注入、会话捕获、Cron 定时

---

## CLI 命令

### 基础命令

```bash
cd ~/.openclaw/skills/openclaw-omg
export PYTHONPATH=src

# 初始化
python3 -m memory_system.cli init

# 添加记忆
python3 -m memory_system.cli add "内容" --type fact

# 即时捕获（自动评分）
python3 -m memory_system.cli capture "内容" --session ID --index N

# 搜索
python3 -m memory_system.cli search "关键词"

# 整合
python3 -m memory_system.cli consolidate

# 状态
python3 -m memory_system.cli status
```

### OpenClaw 集成

```bash
# 查看状态
python3 -m memory_system.cli integration --status

# 注入快照
python3 -m memory_system.cli integration --inject main

# 安装 Cron
python3 -m memory_system.cli integration --install-cron
```

---

## 项目位置

| 类型 | 路径 |
|------|------|
| Skill 代码 | `~/.openclaw/skills/openclaw-omg/` |
| 记忆数据 | `~/.openclaw/memory/openclaw-omg/` |
| 配置文件 | `~/.openclaw/memory/openclaw-omg/config.json` |

---

## 版本

v2.0.0 — 即时捕获 + 关键词触发 + 快照注入 + OpenClaw 集成
