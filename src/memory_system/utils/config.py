#!/usr/bin/env python3
"""
Configuration Manager - 配置管理
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_CONFIG = {
    "version": "1.6.0",
    "memory_dir": "./memory",
    
    # 衰减配置
    "decay_rates": {
        "fact": 0.008,      # 半衰期 ~87 天
        "belief": 0.07,     # 半衰期 ~10 天
        "summary": 0.025,   # 半衰期 ~28 天
        "event": 0.15,      # 半衰期 ~5 天
    },
    
    # 阈值配置
    "thresholds": {
        "archive": 0.3,     # 归档阈值
        "delete": 0.1,      # 删除阈值
        "summary_trigger": 3,  # 触发摘要的数量
    },
    
    # Token 预算
    "token_budget": {
        "layer1_total": 2000,  # Layer 1 总 Token 数
    },
    
    # 整合配置
    "consolidation": {
        "idle_timeout_minutes": 20,
        "fallback_hours": 48,
        "max_memories_per_run": 100,
    },
    
    # 冲突检测
    "conflict_detection": {
        "enabled": True,
        "penalty": 0.2,
    },
    
    # LLM 配置
    "llm": {
        "enabled": True,
        "fallback": True,
        "min_confidence": 0.6,
    },
    
    # 向量检索
    "vector": {
        "enabled": False,
        "provider": "openai",
        "model": "text-embedding-3-small",
        "dimension": 1536,
    },
    
    # 主动记忆
    "proactive": {
        "enabled": True,
        "threshold_confidence": 0.7,
        "threshold_messages": 3,
    },
}


class Config:
    """
    配置管理器
    
    支持：
    - 默认配置
    - 文件持久化
    - 环境变量覆盖
    - 运行时更新
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else None
        self.config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        
        if self.config_path and self.config_path.exists():
            self.load()
    
    def load(self) -> bool:
        """从文件加载配置"""
        if not self.config_path or not self.config_path.exists():
            return False
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                self.config.update(loaded)
            return True
        except (json.JSONDecodeError, IOError):
            return False
    
    def save(self) -> bool:
        """保存配置到文件"""
        if not self.config_path:
            return False
        
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def update(self, data: Dict[str, Any]) -> None:
        """批量更新配置"""
        self._deep_update(self.config, data)
    
    def _deep_update(self, base: Dict, update: Dict) -> None:
        """深度更新字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def reset(self) -> None:
        """重置为默认配置"""
        self.config = DEFAULT_CONFIG.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.config.copy()
    
    def __repr__(self) -> str:
        return f"Config({self.config})"
