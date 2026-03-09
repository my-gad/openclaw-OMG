# OpenClaw-OMG Skill 开发指南

## 📋 目录

- [什么是 Skill](#什么是-skill)
- [安装 Skill](#安装-skill)
- [创建 Skill](#创建-skill)
- [Skill 结构](#skill-结构)
- [示例 Skill](#示例-skill)
- [调试技巧](#调试技巧)

---

## 什么是 Skill

Skill 是 OpenClaw 系统中用于扩展功能的模块化组件。OpenClaw-OMG 本身就是一个完整的记忆系统 Skill，提供了：

- 三层记忆架构
- 实体识别系统
- LLM 智能集成
- 多 Agent 支持
- SQLite 存储后端

---

## 安装 Skill

### 方法 1: 使用安装脚本（推荐）

```bash
cd /home/administrator/.openclaw/workspace/openclaw-OMG
./install.sh
```

### 方法 2: 手动安装

```bash
# 1. 克隆项目
cd /home/administrator/.openclaw/workspace
git clone https://github.com/ktao732084-arch/openclaw-OMG.git
cd openclaw-OMG

# 2. 设置环境变量
export PYTHONPATH=/home/administrator/.openclaw/workspace/openclaw-OMG/src:$PYTHONPATH

# 3. 初始化记忆系统
python3 -m memory_system.cli init

# 4. 验证安装
python3 -m memory_system.cli status
```

### 方法 3: 作为 Python 包安装

```bash
# 添加到 Python 路径
echo "export PYTHONPATH=/home/administrator/.openclaw/workspace/openclaw-OMG/src:\$PYTHONPATH" >> ~/.bashrc
source ~/.bashrc

# 或者在 Python 代码中动态添加
import sys
sys.path.insert(0, '/home/administrator/.openclaw/workspace/openclaw-OMG/src')
```

---

## 创建 Skill

### 创建新的 Skill 目录结构

```bash
# 在 OpenClaw skills 目录下创建
cd ~/.openclaw/skills/
mkdir -p my-skill/{src,tests,docs}

# 创建基本文件
touch my-skill/SKILL.md
touch my-skill/README.md
touch my-skill/src/__init__.py
touch my-skill/src/main.py
```

### SKILL.md 模板

```markdown
# my-skill

## 描述
简要描述这个 Skill 的功能

## 安装
```bash
# 安装步骤
```

## 使用
```python
# 使用示例
```

## 配置
- 配置项 1: 说明
- 配置项 2: 说明

## 依赖
- 依赖包 1
- 依赖包 2
```

---

## Skill 结构

### 标准目录结构

```
my-skill/
├── SKILL.md           # Skill 元数据和说明
├── README.md          # 详细说明
├── requirements.txt   # Python 依赖
├── install.sh         # 安装脚本
├── src/               # 源代码
│   ├── __init__.py
│   └── main.py        # 主模块
├── tests/             # 测试
│   ├── __init__.py
│   └── test_main.py
└── docs/              # 文档
    └── guide.md
```

### SKILL.md 格式

```markdown
# Skill 名称

<description>
Skill 的简要描述
</description>

<location>
~/openclaw/skills/my-skill
</location>

## 功能
- 功能 1
- 功能 2

## 使用方法
```bash
# 命令示例
```
```

---

## 示例 Skill

### 示例 1: 天气查询 Skill

```markdown
# weather-skill

<description>
查询天气信息，支持多城市、多预报
</description>

<location>
~/openclaw/skills/weather-skill
</location>

## 安装
```bash
cd ~/.openclaw/skills
git clone https://github.com/xxx/weather-skill.git
```

## 使用
```python
from weather_skill import WeatherAPI

weather = WeatherAPI(api_key="xxx")
forecast = weather.get_forecast("北京")
print(forecast)
```

## 配置
- `api_key`: 天气 API 密钥
- `default_city`: 默认城市
```

### 示例 2: 文件管理 Skill

```markdown
# file-manager-skill

<description>
文件管理工具，支持创建、删除、移动、搜索文件
</description>

<location>
~/openclaw/skills/file-manager-skill
</location>

## 功能
- 创建文件/目录
- 删除文件/目录
- 移动/复制文件
- 搜索文件
- 批量操作

## 使用
```bash
# 创建文件
python3 -m file_manager create "test.txt"

# 搜索文件
python3 -m file_manager search "*.py"
```
```

---

## 将 OpenClaw-OMG 作为 Skill 使用

### 在 Agent 中使用

```python
# 在 Agent 代码中导入
import sys
sys.path.insert(0, '/home/administrator/.openclaw/workspace/openclaw-OMG/src')

from memory_system import MemoryManager, MemoryType

# 初始化
manager = MemoryManager('./memory')

# 添加记忆
manager.add("这是一条测试记忆", MemoryType.FACT)

# 搜索记忆
results = manager.search("测试")
for r in results:
    print(r.content)
```

### 在多 Agent 环境中使用

```python
from pathlib import Path
from memory_system.multiagent import AgentManager, AgentRole

# 初始化 Agent 管理器
manager = AgentManager(Path('./memory'))

# 注册 Agent
agent_id = manager.register_agent(
    name="记忆助手",
    role=AgentRole.ASSISTANT,
    description="协助管理记忆"
)

# 使用记忆系统
from memory_system.core import MemoryManager
memory = MemoryManager(Path('./memory') / 'agents' / agent_id)
memory.add("Agent 特定记忆", MemoryType.FACT)
```

---

## 调试技巧

### 1. 启用调试日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from memory_system.core import MemoryManager
```

### 2. 检查模块导入

```bash
# 测试导入
python3 -c "from memory_system.core import MemoryManager; print('OK')"

# 检查路径
python3 -c "import sys; print('\\n'.join(sys.path))"
```

### 3. 查看日志文件

```bash
# 查看记忆系统日志
tail -f memory/*.log

# 查看系统日志
journalctl -u openclaw-gateway -f
```

### 4. 测试模式

```bash
# 使用测试配置
export MEMORY_TEST_MODE=1
python3 -m memory_system.cli status
```

---

## 发布 Skill

### 1. 准备发布

```bash
# 确保有以下文件
- SKILL.md (必需)
- README.md
- LICENSE
- requirements.txt (如有依赖)
```

### 2. 发布到 GitHub

```bash
git init
git add .
git commit -m "Initial release"
git push origin main
```

### 3. 添加到 ClawHub

访问 https://clawhub.com 提交你的 Skill。

---

## 最佳实践

### 1. 模块化

将功能拆分为小模块，每个模块<500 行。

### 2. 类型注解

使用完整的类型注解：

```python
from typing import List, Dict, Optional

def add_memory(
    content: str,
    memory_type: MemoryType,
    confidence: float = 0.8
) -> str:
    """添加记忆"""
    pass
```

### 3. 文档字符串

为所有公共函数添加 docstring：

```python
def search(query: str) -> List[MemoryRecord]:
    """
    搜索记忆
    
    Args:
        query: 搜索关键词
    
    Returns:
        匹配的记忆列表
    """
    pass
```

### 4. 单元测试

为关键功能编写测试：

```python
def test_add_memory():
    manager = MemoryManager('./memory')
    record_id = manager.add("测试", MemoryType.FACT)
    assert record_id is not None
```

### 5. 错误处理

优雅处理错误：

```python
try:
    result = risky_operation()
except Exception as e:
    logging.error(f"操作失败：{e}")
    return fallback_value()
```

---

## 相关资源

- [OpenClaw 文档](https://docs.openclaw.ai)
- [ClawHub](https://clawhub.com)
- [示例 Skills](https://github.com/openclaw/skills)

---

**版本**: v1.6.0  
**最后更新**: 2026-03-09  
**维护者**: 运维 - 汪维维 (main)
