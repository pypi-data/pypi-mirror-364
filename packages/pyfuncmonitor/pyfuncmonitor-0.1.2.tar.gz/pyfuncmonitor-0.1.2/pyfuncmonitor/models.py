"""Pydantic models for function monitor."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class MemoryUsage(BaseModel):
    """Memory usage information."""
    before: int = Field(..., description="Memory usage before function execution (bytes)")
    after: int = Field(..., description="Memory usage after function execution (bytes)")
    peak: int = Field(..., description="Peak memory usage during execution (bytes)")
    delta: int = Field(..., description="Memory usage difference (bytes)")


class ExecutionResult(BaseModel):
    """Standard response format for decorated functions."""
    result: Any = Field(None, description="Function execution result")
    status: str = Field(..., description="Execution status: 'success' or 'error'")
    errors: Optional[List[str]] = Field(None, description="List of errors if execution failed")
    execution_time: float = Field(..., description="Function execution time in seconds")
    memory_usage: MemoryUsage = Field(..., description="Memory usage statistics")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    timestamp: str = Field(..., description="Execution timestamp in ISO format")
    function_name: str = Field(..., description="Name of the executed function")
    
    # class Config:
    #     """Pydantic model configuration."""
        # json_serializers = {
        #     datetime: lambda v: v.isoformat()
        # }

    model_config = ConfigDict(
        json_serializers={datetime: lambda v: v.isoformat()}
    )
    
    @classmethod
    def create_success(
        cls,
        result: Any,
        execution_time: float,
        memory_usage: Dict[str, int],
        cpu_usage: float,
        function_name: str
    ) -> "ExecutionResult":
        """Create a successful execution result."""
        return cls(
            result=result,
            status="success",
            errors=None,
            execution_time=execution_time,
            memory_usage=MemoryUsage(**memory_usage),
            cpu_usage=cpu_usage,
            timestamp=datetime.now().isoformat(),
            function_name=function_name
        )
    
    @classmethod
    def create_error(
        cls,
        errors: List[str],
        execution_time: float,
        memory_usage: Dict[str, int],
        cpu_usage: float,
        function_name: str,
        result: Any = None
    ) -> "ExecutionResult":
        """Create an error execution result."""
        return cls(
            result=result,
            status="error",
            errors=errors,
            execution_time=execution_time,
            memory_usage=MemoryUsage(**memory_usage),
            cpu_usage=cpu_usage,
            timestamp=datetime.now().isoformat(),
            function_name=function_name
        )