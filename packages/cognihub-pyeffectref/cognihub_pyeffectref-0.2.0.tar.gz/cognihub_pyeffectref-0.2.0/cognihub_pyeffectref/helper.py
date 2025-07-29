
"""各种帮助函数.

这些函数用于处理函数列表转换为字典,以及从数据推断 TypedDict Schema.
"""
import warnings
from typing import Callable, Any, Optional


def create_actions_dict(
    functions: list[Callable[..., Any]]
) -> dict[str, Callable[..., Any]]:
    """将一个函数列表转换为一个字典.

    其中键是函数名,值是函数本身.

    注意匿名函数不被支持

    此函数不执行任何类型或名称校验,假设所有函数都是有效的.
    """
    def is_valid_function(func: Any) -> tuple[bool, Optional[str]]:
        """检查函数是否有效,返回 (是否有效, 错误信息)"""
        if not callable(func):
            return False, f"对象 '{func}' 不是可调用对象,已跳过."

        if not hasattr(func, '__name__') or not func.__name__ or func.__name__ == '<lambda>':
            return False, f"对象 '{func}' 匿名,已跳过."

        return True, None

    result: dict[str, Callable[..., Any]] = {}
    for func in functions:
        is_valid, error_msg = is_valid_function(func)
        if not is_valid and error_msg:
            warnings.warn(
                error_msg,
                UserWarning,
                stacklevel=2
            )
            continue
        result[func.__name__] = func
    return result
