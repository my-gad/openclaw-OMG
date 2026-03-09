# OpenClaw-OMG v2.0.0

**Optimized Memory Gateway** - AI Agent 三层记忆超系统

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/my-gad/openclaw-omg)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 核心功能

- **三层记忆架构**：工作记忆 → 长期记忆 → 原始日志
- **即时记忆捕获**：自动评分重要性，关键词触发检测
- **自动整合**：每日 Consolidation（7 阶段流程）
- **智能衰减**：基于遗忘曲线的自动衰减机制
- **结构化存储**：Facts / Beliefs / Summaries 分类管理
- **多 Agent 支持**：组织架构、Agent 注册、记忆共享
- **OpenClaw 集成**：快照注入、会话捕获、Cron 定时

---

## 文件结构

```
openclaw-omg/
├── README.md                 # 项目说明
├── CHANGELOG.md              # 版本历史
├── MULTIAGENT.md             # 多 Agent 文档
├── LICENSE                   # 许可证
├── src/memory_system/        # 主包
│   ├── __init__.py           # 版本信息
│   ├── __main__.py           # CLI 入口
│   ├── cli.py                # 命令行接口
│   ├── auto_start.py         # 自动启动
│   │
│   ├── core/                 # 核心层
│   │   ├── memory_manager.py # 记忆管理器 (CRUD)
│   │   ├── memory_capture.py # 即时捕获 (自动评分)
│   │   ├── consolidation.py  # 记忆整合 (7 阶段)
│   │   ├── decay_engine.py   # 衰减引擎
│   │   ├── snapshot_generator.py # 快照生成
│   │   └── schema_v1_3_0.py  # 数据模型
│   │
│   ├── intelligence/         # 智能层
│   │   ├── llm_integration.py     # LLM 集成 (xunfei/nvidia)
│   │   ├── entity_system.py       # 实体识别 (三层)
│   │   ├── conflict_resolver.py   # 冲突消解
│   │   ├── memory_operator.py     # 记忆操作
│   │   └── noise_filter.py        # 噪声过滤
│   │
│   ├── retrieval/            # 检索层
│   │   └── hybrid_search.py  # 混合检索
│   │
│   ├── storage/              # 存储层
│   │   ├── sqlite_backend.py # SQLite 后端 (WAL)
│   │   └── backend_adapter.py # 存储适配器
│   │
│   ├── multiagent/           # 多 Agent 层
│   │   ├── agent_manager.py  # Agent 管理器
│   │   ├── auto_register.py  # 自动注册
│   │   ├── agent_config.py   # Agent 配置
│   │   └── organization.py   # 组织管理
│   │
│   ├── integration/          # OpenClaw 集成
│   │   └── openclaw_integration.py # 快照注入/会话捕获
│   │
│   └── utils/                # 工具层
│       ├── config.py         # 配置管理
│       └── helpers.py        # 辅助函数
│
├── tests/                    # 测试套件
│   ├── test_memory_manager.py
│   ├── test_entity_system.py
│   ├── test_consolidation.py
│   └── test_multiagent.py
│
└── memory/                   # 运行数据
    ├── config.json           # 配置文件
    ├── layer1/               # 工作记忆
    │   └── snapshot.md       # 快照
    ├── layer2/               # 长期记忆
    │   ├── memories.db       # SQLite
    │   ├── pending.jsonl     # 待处理
    │   ├── active/           # 活跃记忆
    │   └── archive/          # 归档
    ├── layer3/               # 原始日志
    ├── agents/               # Agent 数据
    ├── organizations/        # 组织数据
    └── shared_spaces/        # 共享空间
```

---

## 模块功能说明

### core/ - 核心层

| 文件 | 功能 |
|------|------|
| `memory_manager.py` | 记忆 CRUD 操作、搜索、统计 |
| `memory_capture.py` | 即时捕获、重要性评分、关键词触发 |
| `consolidation.py` | 7 阶段记忆整合流程 |
| `decay_engine.py` | 基于遗忘曲线的衰减计算 |
| `snapshot_generator.py` | Layer 1 快照自动生成 |
| `schema_v1_3_0.py` | 数据模型定义 |

### intelligence/ - 智能层

| 文件 | 功能 |
|------|------|
| `llm_integration.py` | LLM 调用 (xunfei/nvidia)、智能触发、失败回退 |
| `entity_system.py` | 三层实体识别 (引号→内置→学习) |
| `conflict_resolver.py` | 记忆冲突检测与消解 |
| `memory_operator.py` | 记忆深度操作 (提取/验证) |
| `noise_filter.py` | 噪声过滤 |

### storage/ - 存储层

| 文件 | 功能 |
|------|------|
| `sqlite_backend.py` | SQLite 后端 (WAL 模式、线程安全) |
| `backend_adapter.py` | 存储抽象接口 |

### multiagent/ - 多 Agent 层

| 文件 | 功能 |
|------|------|
| `agent_manager.py` | Agent 注册、状态管理 |
| `auto_register.py` | 从 OpenClaw 配置自动注册 |
| `agent_config.py` | Agent 配置管理 |
| `organization.py` | 组织架构管理 |

### integration/ - OpenClaw 集成

| 文件 | 功能 |
|------|------|
| `openclaw_integration.py` | 快照注入、会话捕获、Cron 配置 |

---

## 快速开始

```bash
# 克隆项目
git clone https://github.com/my-gad/openclaw-omg.git
cd openclaw-omg

# 初始化
PYTHONPATH=src python3 -m memory_system.cli init

# 添加记忆
python3 -m memory_system.cli add "用户对花生过敏" --type fact

# 即时捕获（自动评分）
python3 -m memory_system.cli capture "我喜欢跑步" --session session1 --index 1

# 搜索
python3 -m memory_system.cli search "花生"

# 整合
python3 -m memory_system.cli consolidate

# 状态
python3 -m memory_system.cli status
```

## OpenClaw 集成

```bash
# 查看集成状态
python3 -m memory_system.cli integration --status

# 注入快照到 Agent
python3 -m memory_system.cli integration --inject main

# 安装 Cron 定时任务
python3 -m memory_system.cli integration --install-cron
```

---

## CLI 命令

| 命令 | 功能 |
|------|------|
| `init` | 初始化 |
| `add "内容"` | 添加记忆 |
| `capture "内容"` | 即时捕获 |
| `search "关键词"` | 搜索 |
| `consolidate` | 记忆整合 |
| `status` | 状态查看 |
| `integration` | OpenClaw 集成 |
| `agent-list` | Agent 列表 |
| `export/import` | 导出/导入 |

---

## LLM 配置

配置文件 `memory/config.json`：

```json
{
  "llm": {
    "enabled": true,
    "provider": "xunfei",
    "model": "xminimaxm25"
  }
}
```

API Key 自动从 `~/.openclaw/openclaw.json` 读取。

---

## 版本历史

### v2.0.0 (2026-03-09)
- 即时记忆捕获 + 自动评分
- 关键词触发检测
- 快照自动生成
- OpenClaw 集成模块
- 移除环境变量依赖

### v1.6.0 (2026-03-09)
- 模块化架构重构
- SQLite 优化

---

**最后更新:** 2026-03-09  
**版本:** v2.0.0
