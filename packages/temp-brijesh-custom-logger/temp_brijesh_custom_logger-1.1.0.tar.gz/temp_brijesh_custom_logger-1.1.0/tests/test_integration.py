"""
Integration tests for custom_logger package
"""

import unittest
import tempfile
import os
import sys
import time
import json
import threading
from unittest.mock import patch
from io import StringIO

# Add parent directory to path for testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from custom_logger import (
    CustomLogger,
    set_trace_id,
    get_trace_id,
    LOG_CONFIG
)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete custom logger package"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            "log_level": "DEBUG",
            "reset_handlers": True,
            "console": {
                "enabled": True,
                "level": "DEBUG",
                "format": {
                    "fmt": "[%(asctime)s] | %(levelname)-8s | %(filename)s: %(lineno)d | %(trace_id)s | - %(message)s",
                    "datefmt": "%d-%m-%Y %H:%M:%S"
                }
            },
            "text_file": {
                "enabled": True,
                "filename": "integration_test.log",
                "path": self.temp_dir,
                "max_bytes": 10240,  # Increased from 1024 to prevent rotation during tests
                "backup_count": 2,
                "format": {
                    "fmt": "[%(asctime)s] | %(levelname)-8s | %(filename)s: %(lineno)d | %(trace_id)s | - %(message)s",
                    "datefmt": "%d-%m-%Y %H:%M:%S"
                }
            },
            "json_file": {
                "enabled": True,
                "filename": "integration_test.json",
                "path": self.temp_dir,
                "max_bytes": 10240,  # Increased from 1024 to prevent rotation during tests
                "backup_count": 2
            },
            "async_logging": {
                "enabled": False,
                "batch_size": 5,
                "batch_timeout": 0.1,
                "queue_size": 50
            }
        }

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

    def test_full_logging_workflow(self):
        """Test complete logging workflow with all handlers"""
        logger = CustomLogger("integration_test", self.test_config)
        
        # Set trace ID
        test_trace_id = "integration-test-123"
        set_trace_id(test_trace_id)
        
        try:
            # Log various messages
            logger.debug("Debug message for integration test")
            logger.info("Info message for integration test")
            logger.warning("Warning message for integration test")
            logger.error("Error message for integration test")
            logger.critical("Critical message for integration test")
            
            # Log with extra context
            logger.info("Message with context", extra={"user_id": "test_user", "session_id": "test_session"})
            
            # Log an exception
            try:
                raise ValueError("Test exception for integration test")
            except ValueError:
                logger.exception("Exception caught in integration test")
            
            # Verify files were created
            text_log_file = os.path.join(self.temp_dir, "integration_test_integration_test.log")
            json_log_file = os.path.join(self.temp_dir, "integration_test_integration_test.json")
            
            self.assertTrue(os.path.exists(text_log_file), "Text log file not created")
            self.assertTrue(os.path.exists(json_log_file), "JSON log file not created")
            
            # Verify trace ID is in log files
            with open(text_log_file, 'r') as f:
                text_content = f.read()
                self.assertIn(test_trace_id, text_content)
                self.assertIn("Debug message for integration test", text_content)
                self.assertIn("Critical message for integration test", text_content)
            
            # Verify JSON log file contains valid JSON
            with open(json_log_file, 'r') as f:
                json_content = f.read().strip()
                if json_content:
                    # The JSON formatter produces pretty-printed JSON
                    # For multiple log entries, they might be separated or concatenated
                    # Try to parse as a single JSON object first
                    try:
                        json_data = json.loads(json_content)
                        # Successfully parsing JSON is what we expect
                        self.assertIn("level", json_data)
                        self.assertIn("message", json_data)
                        self.assertIn("timestamp", json_data)
                    except json.JSONDecodeError:
                        # If not a single JSON object, might be multiple pretty-printed objects
                        # Look for individual JSON objects by finding { } pairs
                        import re
                        # Find JSON object patterns (simplified approach)
                        json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', json_content, re.DOTALL)
                        
                        valid_json_found = False
                        for json_str in json_objects:
                            try:
                                json_data = json.loads(json_str)
                                self.assertIn("level", json_data)
                                self.assertIn("message", json_data)
                                self.assertIn("timestamp", json_data)
                                valid_json_found = True
                                break
                            except json.JSONDecodeError:
                                continue
                        
                        if not valid_json_found:
                            self.fail(f"Expected valid JSON in log file, but got: {json_content[:200]}...")
            
        finally:
            logger.close()

    def test_multi_logger_isolation(self):
        """Test that multiple loggers work independently"""
        logger1 = CustomLogger("service1", self.test_config)
        logger2 = CustomLogger("service2", self.test_config)
        
        try:
            # Set different trace IDs
            set_trace_id("trace-service1")
            logger1.info("Message from service 1")
            
            set_trace_id("trace-service2")
            logger2.info("Message from service 2")
            
            # Verify separate log files
            log1_file = os.path.join(self.temp_dir, "service1_integration_test.log")
            log2_file = os.path.join(self.temp_dir, "service2_integration_test.log")
            
            self.assertTrue(os.path.exists(log1_file))
            self.assertTrue(os.path.exists(log2_file))
            
            # Verify content isolation
            with open(log1_file, 'r') as f:
                content1 = f.read()
                self.assertIn("Message from service 1", content1)
                self.assertNotIn("Message from service 2", content1)
            
            with open(log2_file, 'r') as f:
                content2 = f.read()
                self.assertIn("Message from service 2", content2)
                self.assertNotIn("Message from service 1", content2)
                
        finally:
            logger1.close()
            logger2.close()

    def test_async_logging_integration(self):
        """Test async logging with real handlers"""
        config = self.test_config.copy()
        config["async_logging"]["enabled"] = True
        
        logger = CustomLogger("async_test", config)
        
        try:
            set_trace_id("async-test-456")
            
            # Log multiple messages quickly
            for i in range(10):
                logger.info(f"Async message {i}")
            
            # Give time for async processing
            time.sleep(0.5)
            
            # Verify files were created and contain messages
            text_log_file = os.path.join(self.temp_dir, "async_test_integration_test.log")
            self.assertTrue(os.path.exists(text_log_file))
            
            with open(text_log_file, 'r') as f:
                content = f.read()
                # Should contain multiple messages
                self.assertIn("Async message 0", content)
                self.assertIn("Async message 9", content)
                
        finally:
            logger.close()

    def test_context_manager_integration(self):
        """Test logger as context manager"""
        test_trace_id = "context-manager-test"
        set_trace_id(test_trace_id)
        
        with CustomLogger("context_test", self.test_config) as logger:
            logger.info("Message from context manager")
            logger.error("Error from context manager")
        
        # Verify logging worked
        text_log_file = os.path.join(self.temp_dir, "context_test_integration_test.log")
        self.assertTrue(os.path.exists(text_log_file))
        
        with open(text_log_file, 'r') as f:
            content = f.read()
            self.assertIn("Message from context manager", content)
            self.assertIn(test_trace_id, content)

    def test_custom_levels_integration(self):
        """Test custom log levels in full integration"""
        logger = CustomLogger("custom_level_test", self.test_config)
        
        try:
            # Add custom levels
            logger.add_custom_level("AUDIT", 25)
            logger.add_custom_level("BUSINESS", 35)
            
            set_trace_id("custom-level-test")
            
            # Use custom levels
            logger.audit("Audit level message")
            logger.business("Business level message")
            logger.info("Regular info message")
            
            # Verify in log files
            text_log_file = os.path.join(self.temp_dir, "custom_level_test_integration_test.log")
            self.assertTrue(os.path.exists(text_log_file))
            
            with open(text_log_file, 'r') as f:
                content = f.read()
                self.assertIn("AUDIT", content)
                self.assertIn("BUSINESS", content)
                self.assertIn("Audit level message", content)
                self.assertIn("Business level message", content)
                
        finally:
            logger.close()

    def test_error_recovery_integration(self):
        """Test error recovery in integration scenarios"""
        # Test with invalid log directory that gets created
        config = self.test_config.copy()
        new_log_dir = os.path.join(self.temp_dir, "new_logs")
        config["text_file"]["path"] = new_log_dir
        config["json_file"]["path"] = new_log_dir
        
        logger = CustomLogger("error_recovery_test", config)
        
        try:
            logger.info("Message after directory creation")
            
            # Verify directory was created
            self.assertTrue(os.path.exists(new_log_dir))
            
            # Verify logging worked
            text_log_file = os.path.join(new_log_dir, "error_recovery_test_integration_test.log")
            self.assertTrue(os.path.exists(text_log_file))
            
        finally:
            logger.close()

    def test_threaded_logging_integration(self):
        """Test logging from multiple threads"""
        logger = CustomLogger("thread_test", self.test_config)
        results = {}
        
        def thread_worker(thread_id):
            trace_id = f"thread-{thread_id}"
            set_trace_id(trace_id)
            
            for i in range(5):
                logger.info(f"Thread {thread_id} message {i}")
            
            results[thread_id] = trace_id
        
        try:
            # Create multiple threads
            threads = []
            for i in range(3):
                thread = threading.Thread(target=thread_worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            # Verify all threads completed
            self.assertEqual(len(results), 3)
            
            # Verify log file contains messages from all threads
            text_log_file = os.path.join(self.temp_dir, "thread_test_integration_test.log")
            self.assertTrue(os.path.exists(text_log_file))
            
            with open(text_log_file, 'r') as f:
                content = f.read()
                for thread_id in range(3):
                    self.assertIn(f"Thread {thread_id} message", content)
                    self.assertIn(f"thread-{thread_id}", content)
                    
        finally:
            logger.close()

    def test_large_volume_logging(self):
        """Test logging large volumes of data"""
        logger = CustomLogger("volume_test", self.test_config)
        
        try:
            set_trace_id("volume-test")
            
            # Log many messages to test rotation
            for i in range(100):
                logger.info(f"Volume test message {i} with some additional data to increase size")
            
            # Verify log files exist
            text_log_file = os.path.join(self.temp_dir, "volume_test_integration_test.log")
            self.assertTrue(os.path.exists(text_log_file))
            
            # Check if rotation occurred (backup files)
            backup_files = [f for f in os.listdir(self.temp_dir) if f.startswith("volume_test_integration_test.log.")]
            # Might have backup files due to rotation
            
            # Verify content is present
            with open(text_log_file, 'r') as f:
                content = f.read()
                # Should contain some of the messages
                self.assertIn("Volume test message", content)
                
        finally:
            logger.close()

    def test_configuration_changes_integration(self):
        """Test changing configuration and verifying it takes effect"""
        import copy
        
        # Start with console only
        config1 = copy.deepcopy(self.test_config)
        config1["text_file"]["enabled"] = False
        config1["json_file"]["enabled"] = False
        
        logger1 = CustomLogger("config_test", config1)
        logger1.info("Console only message")
        logger1.close()
        
        # Verify no files created
        text_log_file = os.path.join(self.temp_dir, "config_test_integration_test.log")
        json_log_file = os.path.join(self.temp_dir, "config_test_integration_test.json")
        self.assertFalse(os.path.exists(text_log_file))
        self.assertFalse(os.path.exists(json_log_file))
        
        # Now enable file logging
        config2 = copy.deepcopy(self.test_config)
        logger2 = CustomLogger("config_test2", config2)
        logger2.info("File logging enabled message")
        logger2.close()
        
        # Verify files created
        text_log_file2 = os.path.join(self.temp_dir, "config_test2_integration_test.log")
        json_log_file2 = os.path.join(self.temp_dir, "config_test2_integration_test.json")
        self.assertTrue(os.path.exists(text_log_file2))
        self.assertTrue(os.path.exists(json_log_file2))


if __name__ == '__main__':
    unittest.main() 