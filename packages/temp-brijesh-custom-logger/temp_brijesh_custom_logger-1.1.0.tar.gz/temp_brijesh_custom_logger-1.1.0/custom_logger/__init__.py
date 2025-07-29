"""
Custom Logger Package

A comprehensive logging solution with console, file, JSON, and async logging capabilities.
"""

from .logger import (
    CustomLogger,
    CustomLoggerError,
    ConfigurationError,
    HandlerInitializationError
)
from .logging_components import (
    ConsoleHandler,
    TextFileHandler,
    JSONFileHandler,
    AsyncLogHandler,
    TraceIdFilter,
    set_trace_id,
    get_trace_id
)
from .config import LOG_CONFIG

__version__ = "1.1.0"
__author__ = "Brijesh Turabit"

__all__ = [
    'CustomLogger',
    'CustomLoggerError',
    'ConfigurationError', 
    'HandlerInitializationError',
    'ConsoleHandler',
    'TextFileHandler', 
    'JSONFileHandler',
    'AsyncLogHandler',
    'TraceIdFilter',
    'set_trace_id',
    'get_trace_id',
    'LOG_CONFIG'
]
