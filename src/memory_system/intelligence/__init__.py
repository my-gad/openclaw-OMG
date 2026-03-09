"""
Intelligence - 智能层模块

提供噪音过滤、记忆操作、冲突消解、实体识别、LLM 集成等功能。
"""

from memory_system.intelligence.noise_filter import NoiseFilter
from memory_system.intelligence.memory_operator import MemoryOperator
from memory_system.intelligence.conflict_resolver import ConflictResolver
from memory_system.intelligence.entity_system import EntitySystem
from memory_system.intelligence.llm_integration import (
    detect_semantic_complexity,
    should_use_llm_for_filtering,
    call_llm_with_fallback,
    get_llm_stats,
    reset_llm_stats,
)

__all__ = [
    "NoiseFilter",
    "MemoryOperator",
    "ConflictResolver",
    "EntitySystem",
    "detect_semantic_complexity",
    "should_use_llm_for_filtering",
    "call_llm_with_fallback",
    "get_llm_stats",
    "reset_llm_stats",
]
