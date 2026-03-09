#!/usr/bin/env python3
"""
OpenClaw-OMG v1.6.0 - 主入口文件

整合所有版本的核心功能，提供统一的 API 接口。
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from memory_system import __version__
from memory_system.cli import main as cli_main


def print_banner():
    """打印欢迎横幅"""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║   OpenClaw-OMG v{__version__} - Optimized Memory Gateway          ║
║   AI Agent 记忆超系统                                     ║
╚══════════════════════════════════════════════════════════╝
    """)


def quick_start():
    """快速开始指南"""
    print("""
🚀 快速开始:

1. 初始化记忆系统
   python3 -m memory_system.cli init

2. 添加记忆
   python3 -m memory_system.cli add "这是一条测试记忆" --type fact

3. 搜索记忆
   python3 -m memory_system.cli search "测试"

4. 查看状态
   python3 -m memory_system.cli status

5. 执行记忆整合
   python3 -m memory_system.cli consolidate

📚 更多信息:
   - 文档：./docs/
   - 示例：./examples/
   - 变更日志：./CHANGELOG.md
    """)


if __name__ == "__main__":
    print_banner()
    
    if len(sys.argv) == 1:
        quick_start()
        sys.exit(0)
    
    cli_main()
