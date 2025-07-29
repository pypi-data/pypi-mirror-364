"""
Basic tests for IPC Framework

These tests verify that the package can be imported and basic functionality works.
"""

import unittest
import time
import threading
from ipc_framework import (
    FrameworkServer, 
    FrameworkClient, 
    Application, 
    Channel, 
    Message, 
    MessageType
)


class TestBasicImports(unittest.TestCase):
    """Test that all main classes can be imported"""
    
    def test_imports(self):
        """Test that all main classes are available"""
        self.assertTrue(FrameworkServer)
        self.assertTrue(FrameworkClient)
        self.assertTrue(Application)
        self.assertTrue(Channel)
        self.assertTrue(Message)
        self.assertTrue(MessageType)
    
    def test_message_types(self):
        """Test that all message types are available"""
        self.assertEqual(MessageType.REQUEST.value, "request")
        self.assertEqual(MessageType.RESPONSE.value, "response")
        self.assertEqual(MessageType.NOTIFICATION.value, "notification")
        self.assertEqual(MessageType.PUBLISH.value, "publish")
        self.assertEqual(MessageType.SUBSCRIBE.value, "subscribe")
        self.assertEqual(MessageType.UNSUBSCRIBE.value, "unsubscribe")


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality of the framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.server = FrameworkServer(host="localhost", port=18888)  # Different port for testing
        
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'server') and self.server.running:
            self.server.stop()
    
    def test_server_creation(self):
        """Test that server can be created"""
        self.assertIsInstance(self.server, FrameworkServer)
        self.assertEqual(self.server.host, "localhost")
        self.assertEqual(self.server.port, 18888)
        self.assertFalse(self.server.running)
    
    def test_application_creation(self):
        """Test that applications can be created"""
        app = self.server.create_application("test_app", "Test Application")
        self.assertIsInstance(app, Application)
        self.assertEqual(app.app_id, "test_app")
        self.assertEqual(app.name, "Test Application")
    
    def test_channel_creation(self):
        """Test that channels can be created"""
        app = self.server.create_application("test_app")
        channel = app.create_channel("test_channel")
        self.assertIsInstance(channel, Channel)
        self.assertEqual(channel.channel_id, "test_channel")
        self.assertEqual(channel.app_id, "test_app")
    
    def test_message_creation(self):
        """Test that messages can be created"""
        message = Message(
            message_id="test_msg",
            app_id="test_app",
            channel_id="test_channel",
            message_type=MessageType.REQUEST,
            payload={"test": "data"},
            timestamp=time.time()
        )
        self.assertIsInstance(message, Message)
        self.assertEqual(message.app_id, "test_app")
        self.assertEqual(message.channel_id, "test_channel")
        self.assertEqual(message.message_type, MessageType.REQUEST)
    
    def test_message_serialization(self):
        """Test that messages can be serialized and deserialized"""
        original = Message(
            message_id="test_msg",
            app_id="test_app", 
            channel_id="test_channel",
            message_type=MessageType.REQUEST,
            payload={"test": "data"},
            timestamp=time.time()
        )
        
        # Test to_json and from_json
        json_str = original.to_json()
        self.assertIsInstance(json_str, str)
        
        deserialized = Message.from_json(json_str)
        self.assertEqual(original.message_id, deserialized.message_id)
        self.assertEqual(original.app_id, deserialized.app_id)
        self.assertEqual(original.channel_id, deserialized.channel_id)
        self.assertEqual(original.message_type, deserialized.message_type)
        self.assertEqual(original.payload, deserialized.payload)


if __name__ == '__main__':
    unittest.main() 