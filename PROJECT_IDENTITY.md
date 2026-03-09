# OpenClaw-OMG

**OMG**: Optimized Memory Gateway

## 项目信息

- **原名**: openclaw-OMG
- **现名**: openclaw-OMG
- **版本**: v1.5.0 (重构版)
- **重命名日期**: 2026-03-08
- **作者**: my-gad

## 名称含义

**OMG** 代表 **Optimized Memory Gateway**，寓意：
- 🧠 **优化** (Optimized) - 经过重构和性能优化
- 💾 **记忆** (Memory) - 核心功能是记忆管理
- 🔗 **网关** (Gateway) - 作为 Agent 与记忆之间的智能网关

## 项目状态

✅ 已完成：
- 项目重命名
- 代码结构重构规划
- 新模块结构创建
- CLI 入口优化

🚧 进行中：
- 核心模块拆分
- 类型注解添加
- 测试覆盖提升

## 快速开始

```bash
# 初始化
python3 -m memory_system.cli init

# 添加记忆
python3 -m memory_system.cli add "这是一条测试记忆" --type fact

# 搜索记忆
python3 -m memory_system.cli search "测试"

# 查看状态
python3 -m memory_system.cli status
```

## 目录结构

```
openclaw-OMG/
├── src/memory_system/    # 主包
│   ├── cli.py            # CLI 入口
│   ├── core/             # 核心逻辑
│   ├── storage/          # 存储层
│   ├── retrieval/        # 检索层
│   ├── intelligence/     # 智能层
│   ├── proactive/        # 主动记忆
│   ├── data/             # 数据采集
│   └── utils/            # 工具函数
├── tests/                # 测试
├── docs/                 # 文档
└── examples/             # 示例
```

## 迁移指南

从旧版本迁移：

```bash
# 1. 备份旧数据
cp -r memory/ memory_backup/

# 2. 更新导入
# 旧：from scripts.memory import xxx
# 新：from memory_system import xxx

# 3. 运行迁移工具（如有）
python3 scripts/migrate.py
```

## 相关链接

- GitHub: https://github.com/my-gad/openclaw-OMG
- 文档：./docs/
- 变更日志：./CHANGELOG.md
