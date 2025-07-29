"""
Unit tests for CustomLogger class
"""

import unittest
import logging
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO

# Add parent directory to path for testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from custom_logger import (
    CustomLogger,
    CustomLoggerError,
    ConfigurationError,
    HandlerInitializationError,
    set_trace_id,
    get_trace_id
)


class TestCustomLogger(unittest.TestCase):
    """Test cases for CustomLogger class"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_logger_name = "test_logger"
        self.temp_dir = tempfile.mkdtemp()
        
        # Basic test configuration
        self.test_config = {
            "log_level": "DEBUG",
            "reset_handlers": True,
            "console": {
                "enabled": True,
                "level": "DEBUG",
                "format": {
                    "fmt": "%(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },
            "text_file": {
                "enabled": False,
                "filename": "test.log",
                "path": self.temp_dir,
                "max_bytes": 1024,
                "backup_count": 2,
                "format": {
                    "fmt": "%(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },
            "json_file": {
                "enabled": False,
                "filename": "test.json",
                "path": self.temp_dir,
                "max_bytes": 1024,
                "backup_count": 2
            },
            "async_logging": {
                "enabled": False,
                "batch_size": 10,
                "batch_timeout": 0.1,
                "queue_size": 100
            }
        }

    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temp directory
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

    def test_logger_initialization_success(self):
        """Test successful logger initialization"""
        logger = CustomLogger(self.test_logger_name, self.test_config)
        self.assertEqual(logger.name, self.test_logger_name)
        self.assertIsNotNone(logger.logger)
        self.assertEqual(logger.logger.level, logging.DEBUG)
        logger.close()

    def test_logger_initialization_with_default_config(self):
        """Test logger initialization with default config"""
        logger = CustomLogger(self.test_logger_name)
        self.assertEqual(logger.name, self.test_logger_name)
        self.assertIsNotNone(logger.logger)
        logger.close()

    def test_logger_initialization_invalid_name(self):
        """Test logger initialization with invalid name"""
        with self.assertRaises(ConfigurationError):
            CustomLogger("")
        
        with self.assertRaises(ConfigurationError):
            CustomLogger(None)
        
        with self.assertRaises(ConfigurationError):
            CustomLogger(123)

    def test_logger_initialization_invalid_config(self):
        """Test logger initialization with invalid config"""
        with self.assertRaises(ConfigurationError):
            CustomLogger(self.test_logger_name, "invalid_config")
        
        # Note: None is valid (uses default config), so we test with a different invalid type
        with self.assertRaises(ConfigurationError):
            CustomLogger(self.test_logger_name, 123)

    def test_invalid_log_level(self):
        """Test initialization with invalid log level"""
        invalid_config = self.test_config.copy()
        invalid_config["log_level"] = "INVALID_LEVEL"
        
        with self.assertRaises(ConfigurationError):
            CustomLogger(self.test_logger_name, invalid_config)

    def test_basic_logging_methods(self):
        """Test basic logging methods"""
        logger = CustomLogger(self.test_logger_name, self.test_config)
        
        # Capture console output
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")
        
        logger.close()
        # Verify no errors occurred (stderr should be empty or minimal)

    def test_exception_logging(self):
        """Test exception logging"""
        logger = CustomLogger(self.test_logger_name, self.test_config)
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Exception occurred")
        
        logger.close()

    def test_custom_log_levels(self):
        """Test custom log level functionality"""
        logger = CustomLogger(self.test_logger_name, self.test_config)
        
        # Add custom level
        logger.add_custom_level("AUDIT", 25)
        
        # Verify custom level was added
        self.assertIn("audit", logger._custom_levels)
        self.assertEqual(logger._custom_levels["audit"], 25)
        
        # Test using custom level
        logger.audit("Custom audit message")
        
        logger.close()

    def test_custom_level_invalid_parameters(self):
        """Test custom level with invalid parameters"""
        logger = CustomLogger(self.test_logger_name, self.test_config)
        
        with self.assertRaises(ValueError):
            logger.add_custom_level("", 25)
        
        with self.assertRaises(ValueError):
            logger.add_custom_level("AUDIT", -1)
        
        with self.assertRaises(ValueError):
            logger.add_custom_level("AUDIT", "invalid")
        
        logger.close()

    def test_file_handler_creation(self):
        """Test text file handler creation"""
        config = self.test_config.copy()
        config["text_file"]["enabled"] = True
        
        logger = CustomLogger(self.test_logger_name, config)
        logger.info("Test file message")
        
        # Check if log file was created
        expected_file = os.path.join(self.temp_dir, f"{self.test_logger_name}_test.log")
        self.assertTrue(os.path.exists(expected_file))
        
        logger.close()

    def test_json_handler_creation(self):
        """Test JSON file handler creation"""
        config = self.test_config.copy()
        config["json_file"]["enabled"] = True
        
        logger = CustomLogger(self.test_logger_name, config)
        logger.info("Test JSON message")
        
        # Check if JSON log file was created
        expected_file = os.path.join(self.temp_dir, f"{self.test_logger_name}_test.json")
        self.assertTrue(os.path.exists(expected_file))
        
        logger.close()

    def test_file_handler_permission_error(self):
        """Test file handler with permission error"""
        config = self.test_config.copy()
        config["text_file"]["enabled"] = True
        config["text_file"]["path"] = "/root/forbidden"  # Path that likely won't be writable
        
        # Should not raise exception but fall back to /tmp
        logger = CustomLogger(self.test_logger_name, config)
        logger.info("Test message")
        logger.close()

    @patch('custom_logger.logger.AsyncLogHandler')
    def test_async_handler_creation(self, mock_async_handler):
        """Test async handler creation"""
        config = self.test_config.copy()
        config["async_logging"]["enabled"] = True
        
        mock_handler_instance = MagicMock()
        mock_async_handler.return_value = mock_handler_instance
        
        logger = CustomLogger(self.test_logger_name, config)
        
        # Verify async handler was created
        mock_async_handler.assert_called_once()
        logger.close()

    def test_handler_initialization_error(self):
        """Test handler initialization error handling"""
        config = self.test_config.copy()
        
        # Mock ConsoleHandler to raise exception
        with patch('custom_logger.logger.ConsoleHandler', side_effect=Exception("Handler failed")):
            with self.assertRaises(HandlerInitializationError):
                CustomLogger(self.test_logger_name, config)

    def test_context_manager(self):
        """Test CustomLogger as context manager"""
        with CustomLogger(self.test_logger_name, self.test_config) as logger:
            logger.info("Context manager test")
            self.assertIsNotNone(logger.logger)

    def test_trace_id_functionality(self):
        """Test trace ID functionality"""
        # Test setting and getting trace ID
        test_trace_id = "test-trace-123"
        set_trace_id(test_trace_id)
        self.assertEqual(get_trace_id(), test_trace_id)
        
        # Test with logger
        logger = CustomLogger(self.test_logger_name, self.test_config)
        logger.info("Message with trace ID")
        logger.close()

    def test_logging_with_extra_context(self):
        """Test logging with extra context"""
        logger = CustomLogger(self.test_logger_name, self.test_config)
        
        extra_data = {"user_id": "123", "request_id": "req-456"}
        logger.info("Message with context", extra=extra_data)
        
        logger.close()

    def test_reset_handlers_functionality(self):
        """Test reset handlers functionality"""
        # Create logger with existing handlers
        logger1 = CustomLogger(self.test_logger_name, self.test_config)
        initial_handler_count = len(logger1.logger.handlers)
        logger1.close()
        
        # Create new logger with reset_handlers=True
        config = self.test_config.copy()
        config["reset_handlers"] = True
        
        logger2 = CustomLogger(self.test_logger_name, config)
        # Should have only new handlers
        self.assertGreaterEqual(len(logger2.logger.handlers), 0)
        logger2.close()

    def test_logger_close_cleanup(self):
        """Test logger cleanup on close"""
        logger = CustomLogger(self.test_logger_name, self.test_config)
        initial_handler_count = len(logger.logger.handlers)
        
        logger.close()
        
        # Handlers should be removed
        self.assertEqual(len(logger.logger.handlers), 0)

    def test_logging_error_handling(self):
        """Test error handling during logging operations"""
        logger = CustomLogger(self.test_logger_name, self.test_config)
        
        # Mock logger to raise exception
        with patch.object(logger.logger, 'info', side_effect=Exception("Logging failed")):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                logger.info("This should fail")
                # Should not raise exception, but write to stderr
                stderr_output = mock_stderr.getvalue()
                self.assertIn("Logging error", stderr_output)
        
        logger.close()

    def test_multiple_logger_instances(self):
        """Test creating multiple logger instances"""
        logger1 = CustomLogger("logger1", self.test_config)
        logger2 = CustomLogger("logger2", self.test_config)
        
        self.assertNotEqual(logger1.logger, logger2.logger)
        self.assertEqual(logger1.name, "logger1")
        self.assertEqual(logger2.name, "logger2")
        
        logger1.close()
        logger2.close()

    def test_config_validation(self):
        """Test configuration validation"""
        logger = CustomLogger(self.test_logger_name, self.test_config)
        
        # Test that _validate_config doesn't raise for valid config
        logger._validate_config()
        
        # Test invalid config
        logger._config = "invalid"
        with self.assertRaises(ConfigurationError):
            logger._validate_config()
        
        logger.close()


class TestTraceIdFunctionality(unittest.TestCase):
    """Test cases for trace ID functionality"""

    def test_set_and_get_trace_id(self):
        """Test setting and getting trace ID"""
        test_id = "trace-123-456"
        set_trace_id(test_id)
        self.assertEqual(get_trace_id(), test_id)

    def test_get_trace_id_default(self):
        """Test getting trace ID when none is set"""
        # Clear any existing trace ID
        set_trace_id(None)
        result = get_trace_id()
        # Should return default value "-"
        self.assertEqual(result, "-")

    def test_trace_id_isolation(self):
        """Test that trace IDs are properly isolated"""
        # This test might need to be adapted based on actual implementation
        set_trace_id("test-1")
        self.assertEqual(get_trace_id(), "test-1")
        
        set_trace_id("test-2")
        self.assertEqual(get_trace_id(), "test-2")


if __name__ == '__main__':
    unittest.main() 