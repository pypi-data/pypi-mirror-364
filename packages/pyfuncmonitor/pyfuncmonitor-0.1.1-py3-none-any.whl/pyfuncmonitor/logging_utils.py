"""Logging utilities for function monitor."""

import structlog
from typing import Optional
from logging.handlers import RotatingFileHandler
import logging
import sys

from .config import get_config


def configure_structlog(
    log_level: Optional[int] = None,
    log_to_file: Optional[bool] = None,
    log_file_path: Optional[str] = None
) -> structlog.BoundLogger:
    """Configure structlog with appropriate settings."""
    config = get_config()
    
    # Use provided values or fall back to config
    level = log_level if log_level is not None else config.log_level
    to_file = log_to_file if log_to_file is not None else config.log_to_file
    file_path = log_file_path if log_file_path is not None else config.log_file_path
    
    # Configure standard library logging
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # File handler if requested
    if to_file and file_path:
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=config.log_file_max_size,
            backupCount=config.log_file_backup_count
        )
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)
    
    # Configure structlog processors
    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]
    
    # Add JSON renderer for structured logging
    if to_file:
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Use console renderer for better readability in console
        processors.append(structlog.dev.ConsoleRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger("function_monitor")


# Module-level logger - configured on first import
_logger: Optional[structlog.BoundLogger] = None


def get_logger() -> structlog.BoundLogger:
    """Get the configured logger instance."""
    global _logger
    if _logger is None:
        _logger = configure_structlog()
    return _logger


def reconfigure_logger(**kwargs) -> structlog.BoundLogger:
    """Reconfigure the logger with new settings."""
    global _logger
    _logger = configure_structlog(**kwargs)
    return _logger