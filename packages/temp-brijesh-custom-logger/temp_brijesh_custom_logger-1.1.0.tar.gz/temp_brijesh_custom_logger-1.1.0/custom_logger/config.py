"""
Configuration module for custom logger
"""

LOG_CONFIG = {
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
        "enabled": False,
        "filename": "log_records.log",
        "path": "/var/log/tuva_new",
        "max_bytes": 10485760,
        "backup_count": 3,
        "format": {
            "fmt": "[%(asctime)s] | %(levelname)-8s | %(filename)s: %(lineno)d | %(trace_id)s | - %(message)s",
            "datefmt": "%d-%m-%Y %H:%M:%S"
        }
    },
    "json_file": {
        "enabled": False,
        "filename": "json_log_records.log",
        "path": "/var/log/tuva_new",
        "max_bytes": 10485760,
        "backup_count": 3
    },
    "async_logging": {
        "enabled": False,
        "batch_size": 500,
        "queue_size": 100,
        "batch_timeout": 1.0
    }
} 