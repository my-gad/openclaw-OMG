# OpenClaw-OMG v2.0.0

**Optimized Memory Gateway** - AI Agent 记忆超系统

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/my-gad/openclaw-OMG)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

---

## 📋 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/my-gad/openclaw-OMG.git
cd openclaw-OMG

# 初始化记忆系统
PYTHONPATH=src python3 -m memory_system.cli init
```

### 基本使用

```bash
# 初始化
python3 -m memory_system.cli init

# 添加记忆
python3 -m memory_system.cli add "这是一条测试记忆" --type fact --confidence 0.9

# 即时捕获（自动评分）
python3 -m memory_system.cli capture "用户对花生过敏" --session session123 --index 5

# 搜索记忆
python3 -m memory_system.cli search "测试"

# 执行记忆整合
python3 -m memory_system.cli consolidate

# OpenClaw 集成
python3 -m memory_system.cli integration --status
python3 -m memory_system.cli integration --inject main
python3 -m memory_system.cli integration --install-cron

# 查看状态
python3 -m memory_system.cli status

# 导出/导入
python3 -m memory_system.cli export -o backup.json
python3 -m memory_system.cli import backup.json

# 多 Agent 管理
python3 -m memory_system.cli agent-list
python3 -m memory_system.cli agent-register jiajia --name "执行董事-佳佳"
```

---

## 🎯 核心特性

### 三层记忆架构

```
┌─────────────────────────────────────────┐
│ Layer 1: 工作记忆 (<2000 tokens)        │
│ - Identity / Owner / Top Facts / Recent │
└─────────────────────────────────────────┘
                    ▲
                    │ 按需检索
┌─────────────────────────────────────────┐
│ Layer 2: 结构化长期记忆                  │
│ - facts.jsonl   (确定事实)              │
│ - beliefs.jsonl (推断信念)              │
│ - summaries.jsonl (摘要)                │
│ - entities.json (实体)                  │
└─────────────────────────────────────────┘
                    ▲
                    │ Consolidation 提取
┌─────────────────────────────────────────┐
│ Layer 3: 原始事件日志                    │
│ - 按日期的 MD + JSONL 文件               │
└─────────────────────────────────────────┘
```

### 智能特性

- **实体识别**: 三层识别（引号→内置→学习）
- **语义复杂度**: 自动检测是否需要 LLM
- **智能触发**: 根据置信度决定是否调用 LLM
- **失败回退**: LLM 失败时优雅降级
- **衰减机制**: 基于遗忘曲线的自动衰减
- **记忆整合**: 7 阶段睡眠整理流程

### 技术特性

- **SQLite 存储**: WAL 模式，线程安全
- **混合检索**: 关键词 + 向量（可选）
- **并发安全**: 可重入锁保护
- **TTL 管理**: 自动清理过期数据

---

## 📁 项目结构

```
openclaw-OMG/
├── src/memory_system/        # 主包
│   ├── __init__.py           # 版本：1.6.0
│   ├── cli.py                # CLI 入口
│   ├── core/                 # 核心层
│   │   ├── memory_manager.py
│   │   ├── decay_engine.py
│   │   └── consolidation.py
│   ├── intelligence/         # 智能层
│   │   ├── entity_system.py
│   │   ├── llm_integration.py
│   │   └── ...
│   ├── retrieval/            # 检索层
│   │   └── hybrid_search.py
│   ├── storage/              # 存储层
│   │   └── sqlite_backend.py
│   └── utils/                # 工具层
│       ├── config.py
│       └── helpers.py
├── tests/                    # 单元测试
├── docs/                     # 文档
├── memory/                   # 运行数据
└── README.md                 # 本文件
```

---

## 🧪 测试

```bash
# 运行所有测试
PYTHONPATH=src python3 -m unittest discover tests -v

# 运行特定测试
PYTHONPATH=src python3 -m unittest tests.test_memory_manager -v
```

当前测试覆盖：
- ✅ MemoryManager (CRUD 操作)
- ✅ MemoryRecord (序列化)
- ✅ EntitySystem (实体识别)
- ✅ 混合检索
- ✅ SQLite 后端

---

## 📊 性能指标

| 操作 | 时间 | 说明 |
|------|------|------|
| 初始化 | <100ms | 首次创建数据库 |
| 添加记忆 | ~30ms | SQLite 后端 |
| 搜索记忆 | ~60ms | 混合检索 |
| 导出 100 条 | ~200ms | JSON 格式 |

---

## 🔧 配置

配置文件位于 `memory/config.json`：

```json
{
  "version": "2.0.0",
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
    "min_confidence": 0.6
  }
}
```

---

## 📚 文档

- [PHASE1_COMPLETE.md](docs/PHASE1_COMPLETE.md) - 核心模块拆分
- [PHASE2_COMPLETE.md](docs/PHASE2_COMPLETE.md) - 智能层整合
- [PHASE3_COMPLETE.md](docs/PHASE3_COMPLETE.md) - 存储层优化
- [PROGRESS.md](docs/PROGRESS.md) - 项目进度
- [REFACTOR_SUMMARY.md](docs/REFACTOR_SUMMARY.md) - 重构总结

---

## 🚀 版本历史

### v2.0.0 (2026-03-09)
- ✅ LLM 配置集成 - 自动读取 OpenClaw 主配置
- ✅ 多 Provider 支持 - xunfei / nvidia
- ✅ 自动注册机制 - CLI 执行时自动注册 Agent
- ✅ 即时记忆捕获 - `capture` 命令自动评分
- ✅ 关键词触发检测 - detect_trigger_layer
- ✅ 快照自动生成 - snapshot_generator
- ✅ OpenClaw 集成模块 - 快照注入/会话捕获/Cron
- ✅ Agent 列表同步 - 从 OpenClaw 配置读取
- ✅ 移除环境变量依赖 - 全部配置从文件读取

### v1.6.0 (2026-03-09)
- ✅ 重构为模块化架构
- ✅ 核心层、智能层、检索层、存储层分离
- ✅ 新增实体识别系统
- ✅ 新增 LLM 深度集成
- ✅ SQLite 后端优化（WAL + 线程安全）

### v1.5.0 (2026-03-08)
- 重构计划

### v1.4.0 (2026-02-23)
- 时序引擎

[查看更多](CHANGELOG.md)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

```bash
# 开发环境
git clone https://github.com/my-gad/openclaw-OMG.git
cd openclaw-OMG
pip install -e .

# 运行测试
python3 -m unittest discover tests
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 👤 作者

- **my-gad** - [GitHub](https://github.com/my-gad)

---

## 🔗 相关链接

- GitHub: https://github.com/my-gad/openclaw-OMG
- 文档：https://github.com/my-gad/openclaw-OMG/docs
- 问题反馈：https://github.com/my-gad/openclaw-OMG/issues

---

**最后更新:** 2026-03-09  
**版本:** v2.0.0  
**状态:** ✅ 生产就绪
