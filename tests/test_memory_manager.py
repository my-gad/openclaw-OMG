#!/usr/bin/env python3
"""
单元测试 - Memory Manager
"""

import sys
import unittest
from pathlib import Path
import tempfile
import shutil

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from memory_system.core.memory_manager import MemoryManager, MemoryRecord, MemoryType


class TestMemoryManager(unittest.TestCase):
    """MemoryManager 测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = Path(tempfile.mkdtemp())
        (self.test_dir / "layer2" / "active").mkdir(parents=True, exist_ok=True)
        self.manager = MemoryManager(self.test_dir)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)
    
    def test_add_memory(self):
        """测试添加记忆"""
        record = MemoryRecord(
            content="测试内容",
            memory_type=MemoryType.FACT,
            confidence=0.9
        )
        record_id = self.manager.add(record)
        
        self.assertIsNotNone(record_id)
        self.assertEqual(len(self.manager.get_all()), 1)
    
    def test_get_memory(self):
        """测试获取记忆"""
        record = MemoryRecord(
            content="测试内容",
            memory_type=MemoryType.FACT,
        )
        record_id = self.manager.add(record)
        
        retrieved = self.manager.get(record_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.content, "测试内容")
    
    def test_delete_memory(self):
        """测试删除记忆"""
        record = MemoryRecord(
            content="测试内容",
            memory_type=MemoryType.FACT,
        )
        record_id = self.manager.add(record)
        
        # 删除
        result = self.manager.delete(record_id)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.get_all()), 0)
    
    def test_search_memory(self):
        """测试搜索记忆"""
        # 添加多条记录
        self.manager.add(MemoryRecord(content="苹果很好吃", memory_type=MemoryType.FACT))
        self.manager.add(MemoryRecord(content="香蕉是黄色的", memory_type=MemoryType.FACT))
        self.manager.add(MemoryRecord(content="苹果和香蕉都是水果", memory_type=MemoryType.FACT))
        
        # 搜索"苹果"
        results = self.manager.search("苹果")
        self.assertEqual(len(results), 2)
    
    def test_get_stats(self):
        """测试统计功能"""
        self.manager.add(MemoryRecord(content="事实 1", memory_type=MemoryType.FACT))
        self.manager.add(MemoryRecord(content="事实 2", memory_type=MemoryType.FACT))
        self.manager.add(MemoryRecord(content="信念 1", memory_type=MemoryType.BELIEF))
        
        stats = self.manager.get_stats()
        
        self.assertEqual(stats['facts'], 2)
        self.assertEqual(stats['beliefs'], 1)
        self.assertEqual(stats['total'], 3)


class TestMemoryRecord(unittest.TestCase):
    """MemoryRecord 测试"""
    
    def test_create_record(self):
        """测试创建记录"""
        record = MemoryRecord(
            content="测试内容",
            memory_type=MemoryType.FACT,
            confidence=0.9
        )
        
        self.assertEqual(record.content, "测试内容")
        self.assertEqual(record.memory_type, MemoryType.FACT)
        self.assertEqual(record.confidence, 0.9)
    
    def test_to_dict(self):
        """测试转换为字典"""
        record = MemoryRecord(
            content="测试",
            memory_type=MemoryType.FACT,
        )
        data = record.to_dict()
        
        self.assertIn('id', data)
        self.assertEqual(data['content'], "测试")
        self.assertEqual(data['type'], 'fact')
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            'id': 'test-123',
            'content': '测试内容',
            'type': 'belief',
            'confidence': 0.75,
        }
        record = MemoryRecord.from_dict(data)
        
        self.assertEqual(record.id, 'test-123')
        self.assertEqual(record.content, '测试内容')
        self.assertEqual(record.memory_type, MemoryType.BELIEF)


if __name__ == '__main__':
    unittest.main()
