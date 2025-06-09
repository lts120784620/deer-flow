# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import functools
import json
from typing import Any, Callable, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def ensure_valid_json_output(result: Any) -> str:
    """
    确保工具输出是有效的 JSON 格式。
    
    Args:
        result: 工具的原始输出
        
    Returns:
        格式化后的有效 JSON 字符串
    """
    try:
        if isinstance(result, str):
            # 尝试解析字符串是否已经是 JSON
            try:
                parsed = json.loads(result)
                # 重新序列化以确保格式正确
                return json.dumps(parsed, ensure_ascii=False, separators=(',', ':'))
            except json.JSONDecodeError:
                # 如果不是 JSON，包装成字符串
                return json.dumps({"content": result}, ensure_ascii=False)
        elif isinstance(result, (list, dict)):
            # 直接序列化列表和字典
            return json.dumps(result, ensure_ascii=False, separators=(',', ':'))
        else:
            # 其他类型包装成字符串
            return json.dumps({"content": str(result)}, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Failed to ensure valid JSON output: {e}")
        # 回退到简单的包装
        return json.dumps({"content": str(result), "error": "json_serialization_failed"}, ensure_ascii=False)


def log_io(func: Callable) -> Callable:
    """
    A decorator that logs the input parameters and output of a tool function.

    Args:
        func: The tool function to be decorated

    Returns:
        The wrapped function with input/output logging
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Log input parameters
        func_name = func.__name__
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
        )
        logger.info(f"Tool {func_name} called with parameters: {params}")

        # Execute the function
        result = func(*args, **kwargs)

        # Log the output
        logger.info(f"Tool {func_name} returned: {result}")

        return result

    return wrapper


class LoggedToolMixin:
    """A mixin class that adds logging functionality to any tool."""

    def _log_operation(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """Helper method to log tool operations."""
        tool_name = self.__class__.__name__.replace("Logged", "")
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
        )
        logger.debug(f"Tool {tool_name}.{method_name} called with parameters: {params}")

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Override _run method to add logging."""
        self._log_operation("_run", *args, **kwargs)
        result = super()._run(*args, **kwargs)
        
        # 对于 web_search 工具，确保输出是有效的 JSON
        if hasattr(self, 'name') and self.name == 'web_search':
            result = ensure_valid_json_output(result)
        
        logger.debug(
            f"Tool {self.__class__.__name__.replace('Logged', '')} returned: {result}"
        )
        return result


def create_logged_tool(base_tool_class: Type[T]) -> Type[T]:
    """
    Factory function to create a logged version of any tool class.

    Args:
        base_tool_class: The original tool class to be enhanced with logging

    Returns:
        A new class that inherits from both LoggedToolMixin and the base tool class
    """

    class LoggedTool(LoggedToolMixin, base_tool_class):
        pass

    # Set a more descriptive name for the class
    LoggedTool.__name__ = f"Logged{base_tool_class.__name__}"
    return LoggedTool
