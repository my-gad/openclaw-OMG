#!/usr/bin/env python3
"""
Agent 配置文件管理

每个助手有自己的配置文件，避免环境变量冲突
支持多个助手同时运行
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class AgentConfigData:
    """Agent 配置数据"""
    agent_name: str
    agent_role: str = "assistant"
    agent_description: str = ""
    default_org: Optional[str] = None
    parent_org: Optional[str] = None
    memory_dir: str = "./memory"
    isolated_memory: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "agent_description": self.agent_description,
            "default_org": self.default_org,
            "parent_org": self.parent_org,
            "memory_dir": self.memory_dir,
            "isolated_memory": self.isolated_memory,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfigData":
        return cls(
            agent_name=data.get("agent_name", "未命名助手"),
            agent_role=data.get("agent_role", "assistant"),
            agent_description=data.get("agent_description", ""),
            default_org=data.get("default_org"),
            parent_org=data.get("parent_org"),
            memory_dir=data.get("memory_dir", "./memory"),
            isolated_memory=data.get("isolated_memory", True),
        )


class AgentConfigManager:
    """
    Agent 配置管理器
    
    每个助手有自己的配置文件，互不干扰
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
                        如果未指定，从环境变量 OPENCLAW_CONFIG 读取
                        如果环境变量也未设置，使用默认路径 ./agent_config.json
        """
        if config_path:
            self.config_path = Path(config_path)
        elif os.getenv("OPENCLAW_CONFIG"):
            self.config_path = Path(os.getenv("OPENCLAW_CONFIG"))
        else:
            self.config_path = Path("./agent_config.json")
        
        self._config: Optional[AgentConfigData] = None
        self._load()
    
    def _load(self):
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._config = AgentConfigData.from_dict(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ 加载配置失败：{e}，使用默认配置")
                self._config = AgentConfigData(agent_name="默认助手")
        else:
            # 配置文件不存在，创建默认配置
            self._config = AgentConfigData(agent_name="默认助手")
            self.save()
    
    def save(self):
        """保存配置"""
        if self._config:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, indent=2, ensure_ascii=False)
    
    @property
    def config(self) -> AgentConfigData:
        """获取配置"""
        return self._config
    
    def update(self, **kwargs) -> AgentConfigData:
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        self.save()
        return self._config
    
    @classmethod
    def create_default(cls, config_path: Path, agent_name: str) -> "AgentConfigManager":
        """创建默认配置文件"""
        manager = cls(config_path)
        manager.update(
            agent_name=agent_name,
            agent_description=f"{agent_name} 的默认配置",
        )
        return manager


def get_agent_config(config_path: Optional[Path] = None) -> AgentConfigData:
    """
    获取 Agent 配置（快捷方式）
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        AgentConfigData
    """
    manager = AgentConfigManager(config_path)
    return manager.config


def auto_register_with_config(
    config_path: Optional[Path] = None,
    agent_name: Optional[str] = None,
    org_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    使用配置文件自动注册 Agent
    
    Args:
        config_path: 配置文件路径
        agent_name: 覆盖 Agent 名称
        org_name: 覆盖组织名称
    
    Returns:
        注册结果
    """
    from pathlib import Path
    from memory_system.multiagent.auto_register import quick_setup
    
    # 加载配置
    config_manager = AgentConfigManager(config_path)
    config = config_manager.config
    
    # 使用传入的参数覆盖配置
    name = agent_name or config.agent_name
    org = org_name or config.default_org
    
    try:
        # 自动注册
        result = quick_setup(
            agent_name=name,
            org_name=org,
            parent_org_name=config.parent_org,
            memory_dir=Path(config.memory_dir),
        )
        
        return {
            "success": True,
            "agent_id": result.get("agent_id"),
            "is_new": result.get("is_new", False),
            "org_id": result.get("org_id"),
            "message": "注册成功",
        }
    except Exception as e:
        return {
            "success": False,
            "agent_id": None,
            "is_new": False,
            "org_id": None,
            "message": str(e),
        }


# CLI 入口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent 配置管理")
    parser.add_argument("--config", help="配置文件路径", default="./agent_config.json")
    parser.add_argument("--name", help="Agent 名称")
    parser.add_argument("--role", help="Agent 角色")
    parser.add_argument("--org", help="默认组织")
    parser.add_argument("--show", action="store_true", help="显示当前配置")
    
    args = parser.parse_args()
    
    if args.show:
        # 显示当前配置
        config = get_agent_config(Path(args.config) if args.config else None)
        print("当前配置:")
        print(f"  Agent 名称：{config.agent_name}")
        print(f"  Agent 角色：{config.agent_role}")
        print(f"  默认组织：{config.default_org or '无'}")
        print(f"  记忆目录：{config.memory_dir}")
    elif args.name:
        # 创建/更新配置
        config_path = Path(args.config) if args.config else Path("./agent_config.json")
        manager = AgentConfigManager(config_path)
        
        update_data = {"agent_name": args.name}
        if args.role:
            update_data["agent_role"] = args.role
        if args.org:
            update_data["default_org"] = args.org
        
        manager.update(**update_data)
        print(f"✅ 配置已更新：{config_path}")
    else:
        parser.print_help()
