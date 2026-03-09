#!/usr/bin/env python3
"""
Consolidation Engine - 记忆整合引擎

实现神经科学启发的 7 阶段记忆整合流程。
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from memory_system.core.memory_manager import MemoryManager, MemoryRecord, MemoryType
from memory_system.core.decay_engine import DecayEngine, DecayConfig
from memory_system.intelligence.noise_filter import NoiseFilter
from memory_system.intelligence.memory_operator import MemoryOperator
from memory_system.intelligence.conflict_resolver import ConflictResolver


class ConsolidationConfig:
    """整合配置"""
    def __init__(self):
        # 触发条件
        self.idle_timeout_minutes = 20  # 空闲 20 分钟触发
        self.min_messages_for_consolidation = 3  # 至少 3 条消息
        
        # LLM 配置
        self.llm_enabled = True
        self.llm_fallback = True
        
        # 各阶段配置
        self.phase2_llm_filter = True
        self.phase3_llm_extract = True
        self.phase4b_verify_beliefs = True
        
        # 资源限制
        self.max_memories_per_run = 100
        self.layer1_max_tokens = 2000


class ConsolidationEngine:
    """
    记忆整合引擎
    
    7 阶段整合流程：
    Phase 1: 收集 - 收集团队会话中的原始事件
    Phase 2: 筛选 - 过滤废话，保留有价值内容
    Phase 3: 提取 - 提取关键信息和实体
    Phase 4: 分类 - 分为 Fact/Belief/Summary
    Phase 5: 衰减 - 应用衰减公式
    Phase 6: 归档 - 移动低权重记忆
    Phase 7: 快照 - 生成 Layer 1 快照
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager,
        config: Optional[ConsolidationConfig] = None,
    ):
        self.memory_manager = memory_manager
        self.config = config or ConsolidationConfig()
        self.decay_engine = DecayEngine()
        
        # 可选模块
        self.noise_filter = NoiseFilter()
        self.memory_operator = MemoryOperator()
        self.conflict_resolver = ConflictResolver()
        
        self.last_consolidation_time: Optional[float] = None
    
    def should_consolidate(self, current_time: Optional[float] = None) -> Tuple[bool, str]:
        """
        检查是否应该执行整合
        
        返回：(是否执行，原因)
        """
        current_time = current_time or time.time()
        
        # 检查上次执行时间
        if self.last_consolidation_time:
            elapsed_minutes = (current_time - self.last_consolidation_time) / 60
            if elapsed_minutes < self.config.idle_timeout_minutes:
                return False, f"距离上次整合仅{elapsed_minutes:.1f}分钟"
        
        # 检查是否有新事件
        events = self.memory_manager.get_all(MemoryType.EVENT)
        if not events:
            return False, "无新事件"
        
        return True, f"有{len(events)}个待处理事件"
    
    def run(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行完整整合流程
        
        返回：整合报告
        """
        report = {
            "start_time": datetime.now().isoformat(),
            "phases": {},
            "summary": {
                "processed": 0,
                "kept": 0,
                "archived": 0,
                "deleted": 0,
                "pending_processed": 0,
            }
        }
        
        # 0. 处理待处理队列 (penging → active)
        from memory_system.core.memory_capture import load_pending, save_pending
        pending_path = self.memory_manager.memory_dir / "layer2" / "pending.jsonl"
        if pending_path.exists():
            pending = load_pending(self.memory_manager.memory_dir)
            pending_count = len(pending)
            if pending_count > 0:
                print(f"📦 处理待处理队列: {pending_count} 条")
                for item in pending:
                    # 转换为 MemoryRecord 并添加
                    record = MemoryRecord(
                        content=item["content"],
                        memory_type=MemoryType.FACT,  # 默认 fact，后续分类
                        confidence=item.get("importance", 0.5),
                        source=item.get("source", "pending"),
                    )
                    try:
                        self.memory_manager.add(record)
                        report["summary"]["pending_processed"] = report["summary"].get("pending_processed", 0) + 1
                    except Exception as e:
                        print(f"⚠️ 添加 pending 记忆失败: {e}")
                
                # 清空 pending（已迁移）
                save_pending(self.memory_manager.memory_dir, [])
                print(f" ✅ 待处理队列已清空，{report['summary']['pending_processed']} 条记忆已迁移至 active")
        
        # Phase 1: 收集
        report["phases"]["phase1"] = self._phase1_collect(events)
        
        # Phase 2: 筛选
        filtered, phase2_report = self._phase2_filter(events)
        report["phases"]["phase2"] = phase2_report
        
        # Phase 3: 提取
        extracted, phase3_report = self._phase3_extract(filtered)
        report["phases"]["phase3"] = phase3_report
        
        # Phase 4: 分类
        classified, phase4_report = self._phase4_classify(extracted)
        report["phases"]["phase4"] = phase4_report
        
        # Phase 5: 衰减
        decayed, phase5_report = self._phase5_decay(classified)
        report["phases"]["phase5"] = phase5_report
        
        # Phase 6: 归档
        archived, phase6_report = self._phase6_archive(decayed)
        report["phases"]["phase6"] = phase6_report
        
        # Phase 7: 快照
        phase7_report = self._phase7_snapshot()
        report["phases"]["phase7"] = phase7_report
        
        # 更新统计
        report["summary"]["processed"] = len(events)
        report["end_time"] = datetime.now().isoformat()
        
        self.last_consolidation_time = time.time()
        
        return report
    
    def _phase1_collect(self, events: List[Dict]) -> Dict:
        """Phase 1: 收集原始事件"""
        return {
            "name": "收集",
            "count": len(events),
            "status": "completed",
        }
    
    def _phase2_filter(self, events: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Phase 2: 筛选有价值内容"""
        kept = []
        filtered_count = 0
        
        for event in events:
            content = event.get("content", "")
            
            # 使用废话过滤器（传入完整 event dict）
            is_noise = self.noise_filter.is_noise(event)
            category = "general"  # 默认类别
            
            if is_noise:
                filtered_count += 1
            else:
                kept.append(event)
        
        return kept, {
            "name": "筛选",
            "input": len(events),
            "output": len(kept),
            "filtered": filtered_count,
            "status": "completed",
        }
    
    def _phase3_extract(self, events: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Phase 3: 提取关键信息"""
        extracted = []
        
        for event in events:
            # 简化实现：直接使用原始内容
            # TODO: 使用 LLM 提取关键信息
            extracted.append({
                **event,
                "extracted": True,
            })
        
        return extracted, {
            "name": "提取",
            "count": len(extracted),
            "status": "completed",
        }
    
    def _phase4_classify(self, events: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Phase 4: 分类记忆类型"""
        classified = []
        
        for event in events:
            # 简化：使用关键词判断
            content = event.get("content", "").lower()
            if any(kw in content for kw in ["喜欢", "讨厌", "偏好", "愿意", "不愿意"]):
                memory_type = "belief"  # 信念/偏好
            else:
                memory_type = "fact"    # 事实
            
            classified.append({
                **event,
                "memory_type": memory_type,
            })
        
        return classified, {
            "name": "分类",
            "count": len(classified),
            "status": "completed",
        }
    
    def _phase5_decay(self, items: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Phase 5: 应用衰减"""
        decayed = []
        
        for item in items:
            # 创建临时记录计算衰减
            temp_record = MemoryRecord(
                content=item.get("content", ""),
                memory_type=MemoryType.FACT,
                confidence=item.get("confidence", 0.8),
            )
            
            new_weight = self.decay_engine.calculate_decay(temp_record)
            item["weight"] = new_weight
            decayed.append(item)
        
        return decayed, {
            "name": "衰减",
            "count": len(decayed),
            "status": "completed",
        }
    
    def _phase6_archive(self, items: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Phase 6: 归档低权重记忆"""
        archived_count = 0
        kept = []
        
        for item in items:
            weight = item.get("weight", 1.0)
            
            if weight < 0.3:
                archived_count += 1
                # TODO: 执行归档操作
            else:
                kept.append(item)
                # TODO: 添加到记忆管理器
        
        return kept, {
            "name": "归档",
            "archived": archived_count,
            "kept": len(kept),
            "status": "completed",
        }
    
    def _phase7_snapshot(self) -> Dict:
        """Phase 7: 生成 Layer 1 快照"""
        stats = self.memory_manager.get_stats()
        
        snapshot_content = f"""# 工作记忆快照
生成时间：{datetime.now().isoformat()}

## 统计
- Facts: {stats.get('facts', 0)}
- Beliefs: {stats.get('beliefs', 0)}
- Summaries: {stats.get('summaries', 0)}
- Total: {stats.get('total', 0)}
"""
        
        # 写入快照文件
        snapshot_path = self.memory_manager.memory_dir / "layer1" / "snapshot.md"
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text(snapshot_content, encoding='utf-8')
        
        return {
            "name": "快照",
            "path": str(snapshot_path),
            "status": "completed",
        }
