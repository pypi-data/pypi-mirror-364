import logging
import queue
import threading
import datetime
import inspect
import os
import json
import time
import sys
import traceback

from typing import Any, Dict, List
from logging.handlers import RotatingFileHandler

# For Python 3.10 compatibility
try:
    from datetime import UTC
except ImportError:
    import datetime
    UTC = datetime.timezone.utc


class BaseFormatter(logging.Formatter):
    """Base formatter class with common functionality"""

    def __init__(self, fmt: str, datefmt: str):
        super().__init__(fmt, datefmt)

    @staticmethod
    def get_caller_info() -> Dict[str, Any]:
        """Get the actual caller's information"""
        frame = inspect.currentframe()
        # Skip frames until we find the actual caller
        for _ in range(5):
            if frame:
                frame = frame.f_back

        # Now look for the first frame that's not from logging module
        while frame:
            if not frame.f_code.co_filename.__contains__('logger') and \
                    not frame.f_code.co_filename.__contains__('logging') and \
                    not frame.f_code.co_filename.__contains__('threading'):
                break
            frame = frame.f_back

        if frame:
            return {
                'filename': os.path.split(os.path.dirname(frame.f_code.co_filename))[-1] +
                            "/" + os.path.basename(frame.f_code.co_filename),
                'lineno': frame.f_lineno,
                'function': frame.f_code.co_name,
                'module': frame.f_globals.get('__name__', '')
            }
        return {}

    @staticmethod
    def get_log_data(record: logging.LogRecord) -> logging.LogRecord:
        """Get common log data for all formatters"""
        caller_info = BaseFormatter.get_caller_info()

        record.funcName = caller_info.get('function', record.funcName)
        record.module = caller_info.get('module', record.module)
        record.filename = caller_info.get('filename', record.filename)
        record.lineno = caller_info.get('lineno', record.lineno)

        return record


class ConsoleFormatter(BaseFormatter):
    """Colorized console formatter"""

    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']

        # Get the formatted message using the parent's format method
        formatted_message = super().format(record)

        return f"{level_color}{formatted_message}{reset_color}"


class TextFormatter(BaseFormatter):
    """Simple text formatter for file logging"""

    def format(self, record: logging.LogRecord) -> str:
        return super().format(record)


class JSONFormatter(BaseFormatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        try:
            log_data = {
                'timestamp': datetime.datetime.now(UTC).isoformat(),
                'level': record.levelname,
                'filename': record.filename,
                'line_number': record.lineno,
                'function': record.funcName,
                'module': record.module,
                'message': record.getMessage()
            }

            if hasattr(record, 'extra'):
                log_data.update(record.extra)

            return json.dumps(log_data, indent=2)
        except Exception as e:
            # Fallback to basic format if JSON fails
            return f'{{"error": "JSON formatting failed: {e}", "message": "{record.getMessage()}"}}'


class BaseHandler(logging.Handler):
    """Base handler class with common functionality"""

    def __init__(self, level: int = logging.INFO):
        super().__init__(level)
        self._lock = threading.RLock()


class ConsoleHandler(BaseHandler):
    """Colorized console handler"""

    terminator = "\n"

    def __init__(self, level: int = logging.INFO, fmt: str = None, datefmt: str = None):
        super().__init__(level)
        self.setFormatter(ConsoleFormatter(fmt, datefmt))
        self.stream = sys.stderr

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


class TextFileHandler(RotatingFileHandler):
    """Rotating text file handler"""

    def __init__(
            self,
            filepath: str,
            max_bytes: int = 10 * 1024 * 1024,  # 10MB
            backup_count: int = 5,
            level_name: str = 'INFO',
            fmt: str = None,
            datefmt: str = None
    ):
        # Ensure directory exists
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception:
                pass  # Let the parent handle the error
        
        super().__init__(
            filename=filepath,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        self.setLevel(getattr(logging, level_name, logging.INFO))
        self.setFormatter(TextFormatter(fmt, datefmt))


class JSONFileHandler(RotatingFileHandler):
    """Rotating JSON file handler"""

    def __init__(
            self,
            filepath: str,
            max_bytes: int = 10 * 1024 * 1024,  # 10MB
            backup_count: int = 5,
            level: int = logging.INFO,
            fmt: str = None,
            datefmt: str = None
    ):
        # Ensure directory exists
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception:
                pass  # Let the parent handle the error
        
        super().__init__(
            filename=filepath,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        self.setLevel(level)
        self.setFormatter(JSONFormatter(fmt, datefmt))


class AsyncLogHandler(BaseHandler):
    """
    Asynchronous log handler with batching capabilities.

    This handler collects log records and processes them in batches using a background thread,
    reducing the performance impact of logging on the main application.
    """

    def __init__(
            self,
            batch_size: int = 100,
            batch_timeout: float = 0.1,
            queue_size: int = 10000
    ):
        super().__init__()
        self._handlers: List[logging.Handler] = []
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.queue = queue.Queue(maxsize=queue_size)
        self._stop_event = threading.Event()
        self._worker_thread = None
        self._started = False

    def emit(self, record: logging.LogRecord) -> None:
        """
        Queue a log record for processing by the worker thread.

        Args:
            record: The log record to process
        """
        # Start the worker thread if not already started
        with self._lock:
            if not self._started:
                self.start()

        try:
            # Use a short timeout to prevent blocking indefinitely
            self.queue.put(record)
        except queue.Full:
            # Handle the case where the queue is full
            sys.stderr.write(f"Logging queue full, dropping log record: {record}\n")
            self.handleError(record)

    def add_handler(self, handler: logging.Handler) -> None:
        """
        Add a handler to receive log records.

        Args:
            handler: Handler to add
        """
        with self._lock:
            self._handlers.append(handler)

    def _process_queue(self) -> None:
        """
        Worker thread method to process queued log records in batches.
        """
        batch = []
        last_batch_time = time.time()

        # Continue until stop is signaled
        while not self._stop_event.is_set():
            try:
                # Get record with timeout to allow checking stop_event regularly
                try:
                    record = self.queue.get_nowait()
                    self.queue.task_done()
                    batch.append(record)
                except queue.Empty:
                    # Process any pending records if we've exceeded the timeout
                    if batch:
                        self._flush_records(batch)
                        batch = []
                        last_batch_time = time.time()
                    continue

                # Process batch if size limit reached OR timeout occurred
                if len(batch) >= self.batch_size or (time.time() - last_batch_time >= self.batch_timeout and batch):
                    self._flush_records(batch)
                    batch = []
                    last_batch_time = time.time()

            except Exception as e:
                # Log the error but don't let it crash the worker thread
                error_msg = f"Error in log handler worker thread: {e}\n{traceback.format_exc()}"
                sys.stderr.write(error_msg)

                # Clear the batch to prevent repeated errors with the same records
                batch = []
                time.sleep(1)  # Pause briefly on error to prevent tight error loops

    def _flush_records(self, batch: list) -> None:
        """
        Process a batch of records by sending to all handlers.

        Args:
            batch: List of log records to process
        """
        if not batch:
            return

        # Make a copy of handlers under the lock to avoid modification during iteration
        with self._lock:
            handlers = list(self._handlers)

        # Process each record with each handler
        for record in batch:
            for handler in handlers:
                try:
                    handler.emit(record)
                except Exception as e:
                    sys.stderr.write(f"Error emitting log record to handler {handler}: {e}\n")

    def start(self) -> None:
        """Start the worker thread if not already started."""
        with self._lock:
            if self._started:
                return

            self._stop_event.clear()
            self._worker_thread = threading.Thread(
                target=self._process_queue,
                name="AsyncLogHandler-Worker",
                daemon=True  # Make daemon so it doesn't prevent application exit
            )
            self._worker_thread.start()
            self._started = True
            while True:
                if self._worker_thread.is_alive():
                    break

    def stop(self) -> None:
        """Stop the worker thread and wait for it to terminate."""
        with self._lock:
            if not self._started:
                return

            self._stop_event.set()

            # Wait for the thread to finish with increasing timeouts
            if self._worker_thread and self._worker_thread.is_alive():
                for timeout in [0.5, 1.0, 2.0]:
                    self._worker_thread.join(timeout)
                    if not self._worker_thread.is_alive():
                        break

            self._started = False
            self._worker_thread = None

    def close(self) -> None:
        """Close the handler and process any remaining records."""
        with self._lock:
            if not self._started:
                return

            # Process any remaining records
            try:
                # Move all records from queue to a local list
                remaining_records = []
                while True:
                    try:
                        record = self.queue.get_nowait()
                        self.queue.task_done()
                        remaining_records.append(record)
                    except queue.Empty:
                        break

                # Process the remaining records
                if remaining_records:
                    self._flush_records(remaining_records)
            except Exception as e:
                sys.stderr.write(f"Error processing remaining records during close: {e}\n")

            # Stop the worker thread
            self.stop()

            # Close all handlers
            for handler in self._handlers:
                try:
                    handler.close()
                except Exception as e:
                    sys.stderr.write(f"Error closing handler {handler}: {e}\n")

            # Clear handlers list
            # self._handlers.clear()
            self._started = False

            # Call parent close method
            super().close()


from contextvars import ContextVar

trace_id_ctx_var: ContextVar[str | None] = ContextVar("trace_id", default=None)


def set_trace_id(trace_id: str):
    trace_id_ctx_var.set(trace_id)


def get_trace_id() -> str:
    return trace_id_ctx_var.get() or "-"


class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id()
        BaseFormatter.get_log_data(record)
        return True