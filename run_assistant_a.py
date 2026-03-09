#!/usr/bin/env python3
"""
运维助手启动脚本

使用方法:
    python3 run_assistant_a.py
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# 导入并自动注册
from memory_system.multiagent.agent_config import auto_register_with_config

print("🚀 启动运维助手...")
result = auto_register_with_config(
    config_path=Path("assistants/assistant_a/config.json")
)

if result["success"]:
    print(f"✅ Agent 已就绪")
    print(f"   ID: {result['agent_id']}")
    if result.get("org_id"):
        print(f"   组织：{result['org_id']}")
else:
    print(f"❌ 启动失败：{result['message']}")
    sys.exit(1)

# ... 这里是助手的业务逻辑
print("\n助手运行中...")
