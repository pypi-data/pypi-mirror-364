"""Core monitoring decorator implementation."""

import time
import psutil
import traceback
import inspect
import os
from functools import wraps
from typing import Any, Callable, get_type_hints, Union, Dict, List, Optional

from pydantic import BaseModel, ValidationError

from .config import get_config
from .models import ExecutionResult
from .logging_utils import get_logger


class FunctionMonitor:
    """Function monitoring decorator class."""
    
    def __init__(
        self,
        validate_input: Optional[bool] = None,
        validate_output: Optional[bool] = None,
        log_execution: Optional[bool] = None,
        log_level: Optional[str] = None,
        return_raw_result: Optional[bool] = None,
        enable_memory_monitoring: Optional[bool] = None,
        enable_cpu_monitoring: Optional[bool] = None
    ):
        """Initialize the monitor with configuration options.
        
        Args:
            validate_input: Enable input validation using type hints
            validate_output: Enable output validation using type hints
            log_execution: Enable structured logging
            log_level: Log level for successful executions
            return_raw_result: If True, return original result on success
            enable_memory_monitoring: Enable memory usage monitoring
            enable_cpu_monitoring: Enable CPU usage monitoring
        """
        config = get_config()
        
        self.validate_input = validate_input if validate_input is not None else config.default_validate_input
        self.validate_output = validate_output if validate_output is not None else config.default_validate_output
        self.log_execution = log_execution if log_execution is not None else config.default_log_execution
        self.log_level = log_level if log_level is not None else config.default_log_level
        self.return_raw_result = return_raw_result if return_raw_result is not None else config.default_return_raw_result
        self.enable_memory_monitoring = enable_memory_monitoring if enable_memory_monitoring is not None else config.enable_memory_monitoring
        self.enable_cpu_monitoring = enable_cpu_monitoring if enable_cpu_monitoring is not None else config.enable_cpu_monitoring
        
        self.logger = get_logger()
    
    def __call__(self, func: Callable) -> Callable:
        """Apply monitoring to the function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self._monitor_execution(func, *args, **kwargs)
        return wrapper
    
    def _monitor_execution(self, func: Callable, *args, **kwargs) -> Union[Any, Dict[str, Any]]:
        """Monitor function execution with all enabled features."""
        # Initialize monitoring
        start_time = time.time()
        
        # System monitoring setup
        process = None
        memory_before = 0
        cpu_before = 0.0
        
        try:
            process = psutil.Process(os.getpid())
        except Exception:
            process = None

        if process and self.enable_memory_monitoring:
            try:
                memory_before = process.memory_info().rss
            except Exception:
                self.logger.warning("Unable to read memory info. Disabling memory monitoring.")
                self.enable_memory_monitoring = False

        if process and self.enable_cpu_monitoring:
            try:
                cpu_before = process.cpu_percent()
            except Exception:
                self.logger.warning("Unable to read CPU usage. Disabling CPU monitoring.")
                self.enable_cpu_monitoring = False

        # Get function signature for validation
        sig = inspect.signature(func)
        type_hints = get_type_hints(func) if self.validate_input or self.validate_output else {}
        
        errors: List[str] = []
        result = None
        status = "success"
        
        try:
            # Input validation
            if self.validate_input and type_hints:
                input_errors = self._validate_inputs(func, sig, type_hints, args, kwargs)
                errors.extend(input_errors)
            
            # Execute the function if no input validation errors
            if not errors:
                result = func(*args, **kwargs)
                
                # Output validation
                if self.validate_output and 'return' in type_hints:
                    output_errors = self._validate_output(result, type_hints['return'])
                    if output_errors:
                        errors.extend(output_errors)
                        status = "error"
            else:
                status = "error"
                
        except Exception as e:
            errors.append(f"Execution error: {str(e)}")
            errors.append(f"Traceback: {traceback.format_exc()}")
            status = "error"
            result = None
        
        # Calculate metrics
        end_time = time.time()
        execution_time = end_time - start_time
        
        # System metrics
        memory_usage = self._get_memory_usage(process, memory_before)
        cpu_usage = self._get_cpu_usage(process, cpu_before)
        
        # Create execution result
        if status == "success":
            execution_result = ExecutionResult.create_success(
                result=result,
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                function_name=func.__name__
            )
        else:
            execution_result = ExecutionResult.create_error(
                errors=errors,
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                function_name=func.__name__,
                result=result
            )
        
        # Structured logging
        if self.log_execution:
            self._log_execution(execution_result)
        
        # Return format based on configuration
        if self.return_raw_result and status == "success":
            return result
        else:
            return execution_result.model_dump()
    
    def _validate_inputs(
        self,
        func: Callable,
        sig: inspect.Signature,
        type_hints: Dict[str, Any],
        args: tuple,
        kwargs: Dict[str, Any]
    ) -> List[str]:
        """Validate function inputs against type hints."""
        errors = []
        
        try:
            # Bind arguments to parameters
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each parameter
            for param_name, param_value in bound_args.arguments.items():
                if param_name in type_hints:
                    expected_type = type_hints[param_name]
                    validation_error = self._validate_type(param_value, expected_type, param_name)
                    if validation_error:
                        errors.append(validation_error)
                        
        except Exception as e:
            errors.append(f"Input validation error: {str(e)}")
        
        return errors
    
    def _validate_output(self, result: Any, return_type: Any) -> List[str]:
        """Validate function output against return type hint."""
        errors = []
        validation_error = self._validate_type(result, return_type, "return value")
        if validation_error:
            errors.append(f"Output validation failed: {validation_error}")
        return errors
    
    def _validate_type(self, value: Any, expected_type: Any, param_name: str) -> Optional[str]:
        """Validate a value against an expected type."""
        try:
            # Handle Pydantic models
            if (isinstance(expected_type, type) and 
                issubclass(expected_type, BaseModel)):
                if not isinstance(value, expected_type):
                    if isinstance(value, dict):
                        expected_type(**value)
                    else:
                        expected_type(**value.__dict__)
            # Add more type validation logic here as needed
            
        except ValidationError as e:
            return f"Validation failed for {param_name}: {str(e)}"
        except Exception as e:
            return f"Type validation error for {param_name}: {str(e)}"
        
        return None
    
    def _get_memory_usage(self, process: Optional[psutil.Process], memory_before: int) -> Dict[str, int]:
        """Get memory usage metrics."""
        if not self.enable_memory_monitoring or process is None:
            return {"before": 0, "after": 0, "peak": 0, "delta": 0}
        
        try:
            memory_after = process.memory_info().rss
            return {
                "before": memory_before,
                "after": memory_after,
                "peak": memory_after,  # Simplified - could use peak_rss on some systems
                "delta": memory_after - memory_before
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"before": 0, "after": 0, "peak": 0, "delta": 0}
    
    def _get_cpu_usage(self, process: Optional[psutil.Process], cpu_before: float) -> float:
        """Get CPU usage metrics."""
        if not self.enable_cpu_monitoring or process is None:
            return 0.0
        
        try:
            cpu_after = process.cpu_percent()
            return max(cpu_before, cpu_after)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0
    
    def _log_execution(self, execution_result: ExecutionResult) -> None:
        """Log execution results using structured logging."""
        log_data = execution_result.model_dump()
        
        if execution_result.status == "success":
            if self.log_level.upper() == "DEBUG":
                self.logger.debug("Function executed successfully", **log_data)
            else:
                self.logger.info("Function executed successfully", **log_data)
        else:
            self.logger.error("Function execution failed", **log_data)


# Convenience function for backward compatibility and ease of use
def monitor_function(
    validate_input: bool = True,
    validate_output: bool = True,
    log_execution: bool = True,
    log_level: str = "INFO",
    return_raw_result: bool = False,
    **kwargs
) -> Callable:
    """
    Decorator function for monitoring function execution.
    
    This is the main public API for the function monitor.
    """
    return FunctionMonitor(
        validate_input=validate_input,
        validate_output=validate_output,
        log_execution=log_execution,
        log_level=log_level,
        return_raw_result=return_raw_result,
        **kwargs
    )