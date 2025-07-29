"""ReactiveDict的视图"""
from cognihub_pyeffectref.ref import ReadOnlyRef
from cognihub_pyeffectref.reactive_dict import ReactiveDict
from typing import Any, Dict, NoReturn, Union, Callable

class ReadOnlyView:
    """提供 ReactiveDict 的只读视图.

    插件使用此视图.当访问叶子节点时,返回 ReadOnlyRef.
    当访问嵌套的 ReactiveDict 时,返回 ReadOnlyView.
    """

    def __init__(self, reactive_dict: ReactiveDict):
        if not isinstance(reactive_dict, ReactiveDict):
            raise TypeError("ReadOnlyView 必须包装一个 ReactiveDict 实例.")
        
        self._reactive_dict = reactive_dict
        # _allowed_actions 现在直接存储函数，用于此特定实例
        self._allowed_actions: Dict[str, Callable[..., Any]] = {}

    def __getattr__(self, name: str) -> Union['ReadOnlyView', ReadOnlyRef[Any]]:
        """
        实现点式访问,返回嵌套的 ReadOnlyView 或 ReadOnlyRef.
        """
        # 检查请求的属性是否在底层 ReactiveDict 中存在
        if name not in self._reactive_dict._data_refs:
            raise AttributeError(
                f"'{self.__class__.__name__}' 对象没有属性 '{name}'."
            )

        # 获取底层 ReactiveDict 包装的原始 Ref 对象
        target_ref = self._reactive_dict._data_refs[name]
        value_in_ref = target_ref.value

        # 如果值是 ReactiveDict (意味着是一个嵌套的字典结构)
        if isinstance(value_in_ref, ReactiveDict):
            # 递归地返回一个新的 ReadOnlyView 实例,保持只读和点式访问
            return ReadOnlyView(value_in_ref)

        # 对于所有其他值,包装成 ReadOnlyRef
        else:
            return ReadOnlyRef(target_ref)

    def __getitem__(self, key: str) -> Union['ReadOnlyView', ReadOnlyRef[Any]]:
        """
        允许字典式访问,其行为与 getattr 相同,但 MyPy 对此的支持不如点式访问.
        """
        return self.__getattr__(key)

    # 明确不提供任何修改数据的方法,强制只读
    # 插件试图修改将触发 AttributeError 或 TypeError
    def __setattr__(self, name: str, value: Any) -> None:
        # 允许设置内部私有属性
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            raise AttributeError(f"'{self.__class__.__name__}' 对象是只读的,不允许设置属性 '{name}'.")

    def __setitem__(self, key: str, value: Any) -> NoReturn:
        raise TypeError(f"'{self.__class__.__name__}' 对象是只读的,不允许通过键设置项.")

    def __delitem__(self, key: str) -> NoReturn:
        raise TypeError(f"'{self.__class__.__name__}' 对象是只读的,不允许通过键删除项.")

    def __call__(self) -> Dict[str, Any]:
        """
        将只读视图的内容转换为普通的 Python 字典.
        """
        return self._reactive_dict.to_dict()

    def __len__(self) -> int:
        return len(self._reactive_dict)

    def __iter__(self) -> Any:
        return iter(self._reactive_dict)
