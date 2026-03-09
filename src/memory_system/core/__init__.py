"""
Core - 核心记忆模块

包含记忆管理器、整合引擎、衰减引擎等核心组件。
"""

from memory_system.core.memory_manager import MemoryManager, MemoryRecord, MemoryType
from memory_system.core.decay_engine import DecayEngine, DecayConfig
from memory_system.core.consolidation import ConsolidationEngine, ConsolidationConfig

__all__ = [
    "MemoryManager",
    "MemoryRecord",
    "MemoryType",
    "DecayEngine",
    "DecayConfig",
    "ConsolidationEngine",
    "ConsolidationConfig",
]
