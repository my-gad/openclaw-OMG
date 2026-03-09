#!/usr/bin/env python3
"""
单元测试 - Multi-Agent System
"""

import sys
import unittest
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from memory_system.multiagent.agent_manager import (
    AgentManager,
    AgentConfig,
    AgentRole,
    AgentStatus,
    AgentMessage,
)


class TestAgentManager(unittest.TestCase):
    """AgentManager 测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.manager = AgentManager(self.test_dir)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)
    
    def test_register_agent(self):
        """测试注册 Agent"""
        agent_id = self.manager.register_agent(
            name="测试 Agent",
            role=AgentRole.ASSISTANT,
            description="测试描述"
        )
        
        self.assertIsNotNone(agent_id)
        
        # 验证 Agent 已保存
        agent = self.manager.get_agent(agent_id)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.name, "测试 Agent")
        self.assertEqual(agent.role, AgentRole.ASSISTANT)
    
    def test_unregister_agent(self):
        """测试注销 Agent"""
        agent_id = self.manager.register_agent("测试 Agent")
        
        # 注销
        result = self.manager.unregister_agent(agent_id)
        self.assertTrue(result)
        
        # 验证已删除
        agent = self.manager.get_agent(agent_id)
        self.assertIsNone(agent)
    
    def test_list_agents(self):
        """测试列出 Agent"""
        # 注册多个 Agent
        self.manager.register_agent("Agent 1", role=AgentRole.MAIN)
        self.manager.register_agent("Agent 2", role=AgentRole.ASSISTANT)
        self.manager.register_agent("Agent 3", role=AgentRole.SPECIALIST)
        
        agents = self.manager.list_agents()
        self.assertEqual(len(agents), 3)
    
    def test_update_agent_status(self):
        """测试更新 Agent 状态"""
        agent_id = self.manager.register_agent("测试 Agent")
        
        # 更新为活跃
        result = self.manager.update_agent_status(agent_id, AgentStatus.ACTIVE)
        self.assertTrue(result)
        
        agent = self.manager.get_agent(agent_id)
        self.assertEqual(agent.status, AgentStatus.ACTIVE)
    
    def test_send_message(self):
        """测试发送消息"""
        # 注册两个 Agent
        agent1_id = self.manager.register_agent("发送方")
        agent2_id = self.manager.register_agent("接收方")
        
        # 发送消息
        message_id = self.manager.send_message(
            from_agent=agent1_id,
            to_agent=agent2_id,
            content="测试消息",
            message_type="text"
        )
        
        self.assertIsNotNone(message_id)
        
        # 验证消息已接收
        messages = self.manager.get_messages(agent2_id, mark_as_read=False)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "测试消息")
    
    def test_create_shared_space(self):
        """测试创建共享空间"""
        agent1_id = self.manager.register_agent("Agent 1")
        agent2_id = self.manager.register_agent("Agent 2")
        
        # 创建共享空间
        space_id = self.manager.create_shared_space(
            name="共享空间",
            agents=[agent1_id, agent2_id]
        )
        
        self.assertIsNotNone(space_id)
        
        # 验证 Agent 已加入共享空间
        agent1 = self.manager.get_agent(agent1_id)
        self.assertIn(space_id, agent1.shared_memory_spaces)
    
    def test_get_stats(self):
        """测试统计功能"""
        self.manager.register_agent("Agent 1", role=AgentRole.MAIN)
        self.manager.register_agent("Agent 2", role=AgentRole.ASSISTANT)
        self.manager.register_agent("Agent 3", role=AgentRole.ASSISTANT)
        
        stats = self.manager.get_stats()
        
        self.assertEqual(stats['total_agents'], 3)
        self.assertEqual(stats['roles']['main'], 1)
        self.assertEqual(stats['roles']['assistant'], 2)
    
    def test_agent_isolation(self):
        """测试记忆隔离"""
        agent1_id = self.manager.register_agent("Agent 1", isolated_memory=True)
        agent2_id = self.manager.register_agent("Agent 2", isolated_memory=True)
        
        # 获取各自的记忆路径
        path1 = self.manager.get_agent_memory_path(agent1_id)
        path2 = self.manager.get_agent_memory_path(agent2_id)
        
        # 验证路径不同
        self.assertNotEqual(path1, path2)
        
        # 验证路径包含各自 Agent ID
        self.assertIn(agent1_id, str(path1))
        self.assertIn(agent2_id, str(path2))


class TestAgentMessage(unittest.TestCase):
    """AgentMessage 测试"""
    
    def test_create_message(self):
        """测试创建消息"""
        msg = AgentMessage(
            message_id="test-123",
            from_agent="agent1",
            to_agent="agent2",
            content="测试内容"
        )
        
        self.assertEqual(msg.message_id, "test-123")
        self.assertEqual(msg.from_agent, "agent1")
        self.assertEqual(msg.to_agent, "agent2")
        self.assertEqual(msg.content, "测试内容")
    
    def test_message_to_dict(self):
        """测试消息序列化"""
        msg = AgentMessage(
            message_id="test-123",
            from_agent="agent1",
            to_agent="agent2",
            content="测试"
        )
        data = msg.to_dict()
        
        self.assertEqual(data['message_id'], "test-123")
        self.assertEqual(data['content'], "测试")
    
    def test_message_from_dict(self):
        """测试消息反序列化"""
        data = {
            "message_id": "test-456",
            "from_agent": "sender",
            "to_agent": "receiver",
            "content": "内容",
            "message_type": "request",
        }
        msg = AgentMessage.from_dict(data)
        
        self.assertEqual(msg.message_id, "test-456")
        self.assertEqual(msg.from_agent, "sender")
        self.assertEqual(msg.message_type, "request")


if __name__ == '__main__':
    unittest.main()
