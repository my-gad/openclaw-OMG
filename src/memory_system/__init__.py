"""
Memory System - AI Agent 持久化记忆系统

一个受神经科学启发的三层记忆架构系统。
"""

__version__ = "1.6.0"
__author__ = "my-gad"
__description__ = "AI Agent Memory System inspired by Neuroscience"

# 延迟导入，避免循环导入
__all__ = [
    "MemoryManager",
    "MemoryRecord", 
    "MemoryType",
    "Config",
    "HybridSearchEngine",
    "ConsolidationEngine",
]


def __getattr__(name):
    """延迟加载模块"""
    if name == "Config":
        from memory_system.utils.config import Config
        return Config
    elif name == "MemoryManager":
        from memory_system.core.memory_manager import MemoryManager
        return MemoryManager
    elif name == "MemoryRecord":
        from memory_system.core.memory_manager import MemoryRecord
        return MemoryRecord
    elif name == "MemoryType":
        from memory_system.core.memory_manager import MemoryType
        return MemoryType
    elif name == "HybridSearchEngine":
        from memory_system.retrieval.hybrid_search import HybridSearchEngine
        return HybridSearchEngine
    elif name == "ConsolidationEngine":
        from memory_system.core.consolidation import ConsolidationEngine
        return ConsolidationEngine
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
