"""Configuration management for function monitor."""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, fields


@dataclass
class MonitorConfig:
    """Configuration class for function monitoring."""
    # Logging configuration
    log_level: int = field(default_factory=lambda: int(os.getenv("FUNCTION_MONITOR_LOG_LEVEL", logging.DEBUG)))
    log_to_file: bool = field(default_factory=lambda: os.getenv("FUNCTION_MONITOR_LOG_TO_FILE", "false").lower() == "true")
    log_file_path: Optional[str] = field(default_factory=lambda: os.getenv("FUNCTION_MONITOR_LOG_FILE"))
    log_file_max_size: int = field(default_factory=lambda: int(os.getenv("FUNCTION_MONITOR_LOG_FILE_MAX_SIZE", 10 * 1024 * 1024)))  # 10MB
    log_file_backup_count: int = field(default_factory=lambda: int(os.getenv("FUNCTION_MONITOR_LOG_FILE_BACKUP_COUNT", 5)))
    
    # Monitoring defaults
    default_validate_input: bool = True
    default_validate_output: bool = True
    default_log_execution: bool = True
    default_log_level: str = "INFO"
    default_return_raw_result: bool = False
    
    # Performance settings
    enable_memory_monitoring: bool = True
    enable_cpu_monitoring: bool = True
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        if self.log_to_file and not self.log_file_path:
            # Default log file in user's current working directory
            self.log_file_path = str(Path.cwd() / "function_monitor.log")
        
        # Ensure log directory exists if logging to file
        if self.log_to_file and self.log_file_path:
            log_path = Path(self.log_file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "MonitorConfig":
        """Create config from dictionary."""
        valid_fields = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in config_dict.items() if k in valid_fields})
    
    @classmethod
    def from_env(cls) -> "MonitorConfig":
        """Create config from environment variables."""
        return cls()
    
    def update(self, **kwargs) -> None:
        """Update configuration values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration key: {key}")


# Global configuration instance
_global_config: Optional[MonitorConfig] = None


def get_config() -> MonitorConfig:
    """Get the global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = MonitorConfig.from_env()
    return _global_config


def set_config(config: MonitorConfig) -> None:
    """Set the global configuration instance."""
    global _global_config
    _global_config = config


def configure_monitor(
    log_level: Optional[int] = None,
    log_to_file: Optional[bool] = None,
    log_file_path: Optional[str] = None,
    **kwargs
) -> None:
    """Configure the function monitor globally."""
    config = get_config()
    
    update_dict = {}
    if log_level is not None:
        update_dict["log_level"] = log_level
    if log_to_file is not None:
        update_dict["log_to_file"] = log_to_file
    if log_file_path is not None:
        update_dict["log_file_path"] = log_file_path
    
    update_dict.update(kwargs)
    config.update(**update_dict)