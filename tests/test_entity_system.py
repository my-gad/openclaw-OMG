#!/usr/bin/env python3
"""
单元测试 - Entity System
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from memory_system.intelligence.entity_system import EntitySystem


class TestEntitySystem(unittest.TestCase):
    """EntitySystem 测试"""
    
    def setUp(self):
        self.es = EntitySystem()
    
    def test_extract_quoted_entity(self):
        """测试引号实体提取"""
        entities = self.es.extract_entities('「项目 Alpha」很重要')
        
        quoted = [e for e in entities if e['source'] == 'quote']
        self.assertEqual(len(quoted), 1)
        self.assertEqual(quoted[0]['entity'], '项目 Alpha')
    
    def test_extract_builtin_entity(self):
        """测试内置实体提取"""
        entities = self.es.extract_entities('机器人_1 正在运行')
        
        builtin = [e for e in entities if e['source'] == 'builtin']
        self.assertEqual(len(builtin), 1)
        self.assertEqual(builtin[0]['entity'], '机器人_1')
    
    def test_learn_entity(self):
        """测试实体学习"""
        self.es.learn_entity("新实体")
        self.assertIn("新实体", self.es.learned_entities)
    
    def test_isolation(self):
        """测试竞争性抑制"""
        entities = [
            {'entity': '项目 A', 'confidence': 0.9, 'type': 'test'},
            {'entity': '项目 B', 'confidence': 0.8, 'type': 'test'},
        ]
        
        result = self.es.apply_isolation(entities)
        
        # 相似度低的实体不应该被过度抑制
        self.assertEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()
