"""
Function Monitor - A Python decorator for monitoring function execution.

This package provides decorators for monitoring function execution with features including:
- Execution timing
- Memory and CPU monitoring  
- Exception handling
- Pydantic input/output validation
- Structured logging

Example:
    Basic usage:
    
    ```python
    from function_monitor import monitor_function
    
    @monitor_function()
    def my_function(x: int, y: int) -> int:
        return x + y
    
    result = my_function(1, 2)
    ```
    
    With configuration:
    
    ```python
    from function_monitor import monitor_function, configure_monitor
    
    # Configure globally
    configure_monitor(
        log_to_file=True,
        log_file_path="./my_app.log"
    )
    
    @monitor_function(return_raw_result=True)
    def my_function(x: int) -> int:
        return x * 2
    ```
"""

from .core import monitor_function, FunctionMonitor
from .config import configure_monitor, get_config, set_config, MonitorConfig
from .models import ExecutionResult, MemoryUsage
from .logging_utils import get_logger, reconfigure_logger

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Public API
__all__ = [
    # Main decorator
    "monitor_function",
    "FunctionMonitor",
    
    # Configuration
    "configure_monitor",
    "get_config", 
    "set_config",
    "MonitorConfig",
    
    # Models
    "ExecutionResult",
    "MemoryUsage",
    
    # Logging utilities
    "get_logger",
    "reconfigure_logger",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
]