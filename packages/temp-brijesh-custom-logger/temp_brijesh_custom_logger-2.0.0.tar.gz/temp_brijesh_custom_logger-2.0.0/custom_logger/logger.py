import logging
from typing import Dict, Any
from .logging_components import (
    ConsoleHandler,
    TextFileHandler,
    JSONFileHandler,
    AsyncLogHandler, TraceIdFilter
)


class CustomLogger:
    """Main logger class that combines all handlers and formatters"""

    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize the logger with configuration

        Args:
            config (Dict[str, Any]): Configuration dictionary containing:
                - console: dict (console logging settings)
                    - enabled: bool
                    - level: str
                    - format: dict
                        - fmt: str
                        - datefmt: str
                - text_file: dict (text file logging settings)
                    - enabled: bool
                    - path: str
                    - max_bytes: int
                    - backup_count: int
                    - format: dict
                        - fmt: str
                        - datefmt: str
                - json_file: dict (JSON file logging settings)
                    - enabled: bool
                    - path: str
                    - max_bytes: int
                    - backup_count: int
                    - format: dict
                        - fmt: str
                        - datefmt: str
                - async_logging: dict (async logging settings)
                    - enabled: bool
                    - batch_size: int
                    - batch_timeout: float
                    - queue_size: int
        """
        self._config = config
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.get('log_level', 'INFO')))

        # Remove existing handlers
        if config.get('reset_handlers', False):
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)

        # Initialize handlers
        self._init_handlers()

        # Store custom levels
        self._custom_levels = {}
        self._handlers = []

    def _init_handlers(self) -> None:
        """Initialize logging handlers based on configuration."""
        handlers = []

        # Console handler
        if self._config.get("console", {}).get("enabled", True):
            console_handler = ConsoleHandler(
                level=self._config["console"].get("level", "DEBUG"),
                fmt=self._config["console"].get("format", {})['fmt'],
                datefmt=self._config["console"].get("format", {})['datefmt']
            )
            handlers.append(console_handler)

        # Text file handler
        text_config = self._config.get("text_file", {})
        if text_config.get("enabled", False):
            filepath = f"{text_config['path']}/{self.logger.name}_{text_config['filename']}"
            text_handler = TextFileHandler(
                filepath=filepath,
                max_bytes=text_config.get("max_bytes", 1024 * 1024),
                backup_count=text_config.get("backup_count", 5),
                level_name=self._config['log_level'],
                fmt=text_config.get("format", {})['fmt'],
                datefmt=text_config.get("format", {})['datefmt']
            )
            handlers.append(text_handler)

        # JSON file handler
        json_config = self._config.get("json_file", {})
        if json_config.get("enabled", False):
            filepath = f"{text_config['path']}/{self.logger.name}_{text_config['filename']}"
            json_handler = JSONFileHandler(
                filepath=filepath,
                max_bytes=json_config.get("max_bytes", 1024 * 1024),
                backup_count=json_config.get("backup_count", 5),
                level=self._config['log_level']
            )
            handlers.append(json_handler)

        # Async handler
        if self._config.get("async_logging", {}).get("enabled", False):
            async_handler = AsyncLogHandler(
                batch_size=self._config["async_logging"].get("batch_size", 100),
                batch_timeout=self._config["async_logging"].get("batch_timeout", 1.0),
                queue_size=self._config["async_logging"].get("queue_size", 10000)
            )
            for handler in handlers:
                # handler.addFilter(TraceIdFilter())
                async_handler.addFilter(TraceIdFilter())
                async_handler.add_handler(handler)
            self.logger.addHandler(async_handler)
            self._handlers = async_handler
        else:
            self._handlers = handlers
            for handler in handlers:
                handler.addFilter(TraceIdFilter())
                self.logger.addHandler(handler)

    def add_custom_level(self, name: str, level: int) -> None:
        """Add a custom log level and create corresponding logging method."""
        # Add the level to logging
        logging.addLevelName(level, name.upper())

        # Store the custom level
        self._custom_levels[name.lower()] = level

        # Create a method for this level
        def log_method(msg, *args, **kwargs):
            if self.logger.isEnabledFor(level):
                self.logger._log(level, msg, args, **kwargs)

        # Add the method to the logger instance
        setattr(self, name.lower(), log_method)

    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """Log info message."""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """Log error message."""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log exception with traceback."""
        self.logger.exception(msg, *args, **kwargs)

    def close(self) -> None:
        """Close all handlers."""
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)