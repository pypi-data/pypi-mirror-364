import logging
import os
import sys
from typing import Dict, Optional, Any
from .logging_components import (
    ConsoleHandler,
    TextFileHandler,
    JSONFileHandler,
    AsyncLogHandler, 
    TraceIdFilter
)
from .config import LOG_CONFIG


class CustomLoggerError(Exception):
    """Base exception for CustomLogger errors"""
    pass


class ConfigurationError(CustomLoggerError):
    """Raised when there's an error in logger configuration"""
    pass


class HandlerInitializationError(CustomLoggerError):
    """Raised when a handler fails to initialize"""
    pass


class CustomLogger:
    """Main logger class that combines all handlers and formatters"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the logger with configuration

        Args:
            name (str): Logger name
            config (Optional[Dict[str, Any]]): Configuration dictionary. If None, uses default LOG_CONFIG

        Raises:
            ConfigurationError: If configuration is invalid
            HandlerInitializationError: If handlers fail to initialize
        """
        try:
            if not name or not isinstance(name, str):
                raise ConfigurationError("Logger name must be a non-empty string")
            
            self.name = name
            self._config = config if config is not None else LOG_CONFIG
            
            # Validate configuration
            self._validate_config()
            
            # Initialize logger
            self.logger = logging.getLogger(name)
            
            # Set log level with validation
            log_level = self._config.get('log_level', 'INFO')
            if hasattr(logging, log_level):
                self.logger.setLevel(getattr(logging, log_level))
            else:
                self.logger.setLevel(logging.INFO)
                self.logger.warning(f"Invalid log level '{log_level}', defaulting to INFO")

            # Remove existing handlers if requested
            if self._config.get('reset_handlers', False):
                for handler in self.logger.handlers[:]:
                    try:
                        self.logger.removeHandler(handler)
                        handler.close()
                    except Exception as e:
                        # Log warning but continue
                        print(f"Warning: Failed to remove handler: {e}", file=sys.stderr)

            # Initialize handlers
            self._init_handlers()

            # Store custom levels
            self._custom_levels = {}
            self._handlers = []

        except Exception as e:
            if isinstance(e, CustomLoggerError):
                raise
            raise CustomLoggerError(f"Failed to initialize CustomLogger: {e}") from e

    def _validate_config(self) -> None:
        """Validate the configuration dictionary"""
        if not isinstance(self._config, dict):
            raise ConfigurationError("Configuration must be a dictionary")
        
        # Validate log level
        log_level = self._config.get('log_level', 'INFO')
        if not hasattr(logging, log_level):
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            raise ConfigurationError(f"Invalid log level '{log_level}'. Must be one of: {valid_levels}")

    def _init_handlers(self) -> None:
        """Initialize logging handlers based on configuration."""
        handlers = []

        try:
            # Console handler
            if self._config.get("console", {}).get("enabled", True):
                try:
                    console_config = self._config.get("console", {})
                    console_handler = ConsoleHandler(
                        level=console_config.get("level", "DEBUG"),
                        fmt=console_config.get("format", {}).get('fmt', 
                            "[%(asctime)s] | %(levelname)-8s | %(filename)s: %(lineno)d | %(trace_id)s | - %(message)s"),
                        datefmt=console_config.get("format", {}).get('datefmt', "%d-%m-%Y %H:%M:%S")
                    )
                    handlers.append(console_handler)
                except Exception as e:
                    raise HandlerInitializationError(f"Failed to initialize console handler: {e}") from e

            # Text file handler
            text_config = self._config.get("text_file", {})
            if text_config.get("enabled", False):
                try:
                    # Ensure directory exists
                    log_path = text_config.get('path', '/tmp')
                    if not os.path.exists(log_path):
                        try:
                            os.makedirs(log_path, exist_ok=True)
                        except PermissionError:
                            log_path = '/tmp'  # Fallback to /tmp
                            self.logger.warning(f"Cannot create log directory, using {log_path}")
                    
                    filepath = os.path.join(log_path, f"{self.name}_{text_config.get('filename', 'app.log')}")
                    text_handler = TextFileHandler(
                        filepath=filepath,
                        max_bytes=text_config.get("max_bytes", 1024 * 1024),
                        backup_count=text_config.get("backup_count", 5),
                        level_name=self._config.get('log_level', 'INFO'),
                        fmt=text_config.get("format", {}).get('fmt', 
                            "[%(asctime)s] | %(levelname)-8s | %(filename)s: %(lineno)d | %(trace_id)s | - %(message)s"),
                        datefmt=text_config.get("format", {}).get('datefmt', "%d-%m-%Y %H:%M:%S")
                    )
                    handlers.append(text_handler)
                except Exception as e:
                    raise HandlerInitializationError(f"Failed to initialize text file handler: {e}") from e

            # JSON file handler
            json_config = self._config.get("json_file", {})
            if json_config.get("enabled", False):
                try:
                    # Ensure directory exists
                    log_path = json_config.get('path', '/tmp')
                    if not os.path.exists(log_path):
                        try:
                            os.makedirs(log_path, exist_ok=True)
                        except PermissionError:
                            log_path = '/tmp'  # Fallback to /tmp
                            self.logger.warning(f"Cannot create log directory, using {log_path}")
                    
                    filepath = os.path.join(log_path, f"{self.name}_{json_config.get('filename', 'app.json')}")
                    json_handler = JSONFileHandler(
                        filepath=filepath,
                        max_bytes=json_config.get("max_bytes", 1024 * 1024),
                        backup_count=json_config.get("backup_count", 5),
                        level=getattr(logging, self._config.get('log_level', 'INFO'))
                    )
                    handlers.append(json_handler)
                except Exception as e:
                    raise HandlerInitializationError(f"Failed to initialize JSON file handler: {e}") from e

            # Async handler
            if self._config.get("async_logging", {}).get("enabled", False):
                try:
                    async_config = self._config.get("async_logging", {})
                    async_handler = AsyncLogHandler(
                        batch_size=async_config.get("batch_size", 100),
                        batch_timeout=async_config.get("batch_timeout", 1.0),
                        queue_size=async_config.get("queue_size", 10000)
                    )
                    for handler in handlers:
                        async_handler.addFilter(TraceIdFilter())
                        async_handler.add_handler(handler)
                    self.logger.addHandler(async_handler)
                    self._handlers = [async_handler]
                except Exception as e:
                    raise HandlerInitializationError(f"Failed to initialize async handler: {e}") from e
            else:
                self._handlers = handlers
                for handler in handlers:
                    try:
                        handler.addFilter(TraceIdFilter())
                        self.logger.addHandler(handler)
                    except Exception as e:
                        self.logger.warning(f"Failed to add handler {handler}: {e}")

        except HandlerInitializationError:
            raise
        except Exception as e:
            raise HandlerInitializationError(f"Unexpected error during handler initialization: {e}") from e

    def add_custom_level(self, name: str, level: int) -> None:
        """
        Add a custom log level and create corresponding logging method.
        
        Args:
            name (str): Name of the custom level
            level (int): Numeric level value
            
        Raises:
            ValueError: If name or level is invalid
        """
        try:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Level name must be a non-empty string")
            
            if not isinstance(level, int) or level < 0:
                raise ValueError("Level must be a non-negative integer")
            
            # Check if level already exists
            if name.lower() in self._custom_levels:
                self.logger.warning(f"Custom level '{name}' already exists, overwriting")
            
            # Add the level to logging
            logging.addLevelName(level, name.upper())

            # Store the custom level
            self._custom_levels[name.lower()] = level

            # Create a method for this level
            def log_method(msg, *args, **kwargs):
                try:
                    if self.logger.isEnabledFor(level):
                        self.logger._log(level, msg, args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error logging custom level message: {e}")

            # Add the method to the logger instance
            setattr(self, name.lower(), log_method)
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to add custom level: {e}") from e

    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log debug message."""
        try:
            self.logger.debug(msg, *args, **kwargs)
        except Exception as e:
            self._handle_logging_error("debug", msg, e)

    def info(self, msg: str, *args, **kwargs) -> None:
        """Log info message."""
        try:
            self.logger.info(msg, *args, **kwargs)
        except Exception as e:
            self._handle_logging_error("info", msg, e)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log warning message."""
        try:
            self.logger.warning(msg, *args, **kwargs)
        except Exception as e:
            self._handle_logging_error("warning", msg, e)

    def error(self, msg: str, *args, **kwargs) -> None:
        """Log error message."""
        try:
            self.logger.error(msg, *args, **kwargs)
        except Exception as e:
            self._handle_logging_error("error", msg, e)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log critical message."""
        try:
            self.logger.critical(msg, *args, **kwargs)
        except Exception as e:
            self._handle_logging_error("critical", msg, e)

    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log exception with traceback."""
        try:
            self.logger.exception(msg, *args, **kwargs)
        except Exception as e:
            self._handle_logging_error("exception", msg, e)

    def _handle_logging_error(self, level: str, msg: str, error: Exception) -> None:
        """Handle errors that occur during logging"""
        try:
            error_msg = f"Logging error at {level} level: {error}"
            print(error_msg, file=sys.stderr)
            # Try to log to stderr as fallback
            print(f"Original message: {msg}", file=sys.stderr)
        except Exception:
            # If even stderr fails, there's not much we can do
            pass

    def close(self) -> None:
        """Close all handlers and clean up resources."""
        try:
            for handler in self.logger.handlers[:]:
                try:
                    handler.close()
                    self.logger.removeHandler(handler)
                except Exception as e:
                    print(f"Error closing handler {handler}: {e}", file=sys.stderr)
            
            # Close async handler if it exists
            if hasattr(self, '_handlers'):
                for handler in self._handlers:
                    if hasattr(handler, 'close'):
                        try:
                            handler.close()
                        except Exception as e:
                            print(f"Error closing async handler: {e}", file=sys.stderr)
                            
        except Exception as e:
            print(f"Error during logger cleanup: {e}", file=sys.stderr)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure cleanup"""
        self.close()