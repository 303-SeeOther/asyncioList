from __future__ import annotations

"""asyncioList - 异步列表实现

提供线程安全的异步列表操作，支持并发控制和异步迭代。

作者: 303_SeeOther
邮箱: l.z.cheng.1106@gmail.com
版本: 1.0
"""
import asyncio
from typing import List, Optional, Any, AsyncIterator, TypeVar, Generic
import warnings
T = TypeVar('T')


from .exceptions import AsyncioListError, IndexOutOfBoundsError


class AsyncioList(Generic[T]):
    """异步列表类，支持异步迭代和并发操作"""
    def __init__(self, initial_list: Optional[List[T]] = None):
        """初始化AsyncioList实例

        Args:
            initial_list: 初始列表数据，可选
        """
        if initial_list is not None and not isinstance(initial_list, list):
            raise TypeError("initial_list必须是列表类型或None")
        self._items: List[T] = list(initial_list) if initial_list is not None else []
        self._lock: asyncio.Lock = asyncio.Lock()
        self._change_event: asyncio.Event = asyncio.Event()

    def __repr__(self) -> str:
        """返回对象的字符串表示，用于调试"""
        return f"AsyncioList(items={self._items!r})"

    async def is_empty(self) -> bool:
        """检查列表是否为空

        Returns:
            bool: 如果列表为空则返回True，否则返回False
        """
        return await self.length() == 0

    async def append(self, item: T) -> 'AsyncioList[T]':
        """异步添加元素到列表末尾"""
        async with self._lock:
            self._items.append(item)
            # 只在事件未设置时才触发，避免不必要的唤醒
            if not self._change_event.is_set():
                self._change_event.set()
        return self

    async def extend(self, items: List[T]) -> 'AsyncioList[T]':
        """异步扩展列表"""
        if not items:
            return
        async with self._lock:
            self._items.extend(items)
            self._change_event.set()

    async def insert(self, index: int, item: T) -> 'AsyncioList[T]':
        """异步在指定位置插入元素"""
        async with self._lock:
            try:
                self._items.insert(index, item)
            except IndexError as e:
                raise IndexOutOfBoundsError(f"索引 {index} 超出列表范围，当前列表长度为 {len(self._items)}") from e
            self._change_event.set()

    async def remove(self, item: T) -> 'AsyncioList[T]':
        """异步移除第一个出现的元素"""
        async with self._lock:
            try:
                self._items.remove(item)
            except ValueError as e:
                raise AsyncioListError(f"元素 {item} 不在列表中") from e
            self._change_event.set()

    async def pop(self, index: int = -1) -> T:
        """异步移除并返回指定位置的元素

        Args:
            index: 要移除的元素索引，默认为-1（最后一个元素）

        Returns:
            T: 被移除的元素

        Raises:
            IndexError: 如果索引超出范围
        """
        async with self._lock:
            try:
                result = self._items.pop(index)
                if not self._change_event.is_set():
                    self._change_event.set()
                return result
            except IndexError as e:
                raise IndexOutOfBoundsError(f"索引 {index} 超出列表范围，当前列表长度为 {len(self._items)}") from e

    async def clear(self) -> 'AsyncioList[T]':
        """异步清空列表"""
        async with self._lock:
            self._items.clear()
            self._change_event.set()

    async def index(self, item: Any, start: int = 0, end: Optional[int] = None) -> int:
        """异步返回元素第一次出现的索引"""
        async with self._lock:
            try:
                if end is None:
                    return self._items.index(item, start)
                else:
                    return self._items.index(item, start, end)
            except ValueError as e:
                raise AsyncioListError(f"元素 {item} 不在列表中") from e

    async def count(self, item: T) -> int:
        """异步返回元素出现的次数"""
        async with self._lock:
            return self._items.count(item)

    async def contains(self, item: T) -> bool:
        """异步检查元素是否存在于列表中"""
        async with self._lock:
            return item in self._items

    async def slice(self, start: int, stop: int, step: int = 1) -> List[T]:
        """异步获取列表切片"""
        async with self._lock:
            return self._items[start:stop:step]

    async def reverse(self) -> 'AsyncioList[T]':
        """异步反转列表并返回自身以支持链式调用"""
        async with self._lock:
            self._items.reverse()
            self._change_event.set()
        return self

    async def sort(self, **kwargs) -> 'AsyncioList[T]':
        """异步排序列表并返回自身以支持链式调用"""
        async with self._lock:
            self._items.sort(** kwargs)
            self._change_event.set()
        return self

    async def get(self, index: int) -> T:
        """异步获取指定索引的元素

        Args:
            index: 获取元素的索引

        Returns:
            T: 指定索引处的元素

        Raises:
            IndexOutOfBoundsError: 如果索引超出范围
        """
        async with self._lock:
            if index < 0 or index >= len(self._items):
                raise IndexOutOfBoundsError(f"索引 {index} 超出列表范围，当前列表长度为 {len(self._items)}")
            return self._items[index]

    def __len__(self) -> int:
        """返回列表长度（同步方法，支持len()调用）

        注意：在异步环境中可能返回过时数据，建议使用异步的length()方法
        """
        
        warnings.warn("使用同步len()方法可能返回过时数据，建议使用异步length()方法", stacklevel=2)
        return len(self._items)

    async def length(self) -> int:
        """异步返回列表长度

        Returns:
            int: 当前列表中的元素数量
        """
        async with self._lock:
            return len(self._items)


    async def delete_all(self, item: T) -> 'AsyncioList[T]':
        """异步删除所有与传入对象相等的元素"""
        async with self._lock:
            self._items = [i for i in self._items if i != item]
            self._change_event.set()

    async def __aiter__(self) -> AsyncIterator[T]:
        """异步迭代器支持

        注意：迭代过程中不会反映迭代开始后的列表变化
        """
        async with self._lock:
            # 创建当前状态的快照进行迭代
            items = list(self._items)
        for item in items:
            yield item

    async def wait_for_change(self, timeout: Optional[float] = None) -> bool:
        """等待列表发生变化

        Args:
            timeout: 超时时间（秒），None表示无限等待

        Returns:
            bool: 如果事件被触发则返回True，如果超时则返回False
        """
        try:
            await asyncio.wait_for(self._change_event.wait(), timeout)
            return True
        except asyncio.TimeoutError:
            return False
        finally:
            # 重置事件，为下一次等待做准备
            self._change_event.clear()

    async def __aenter__(self) -> 'AsyncioList[T]':
        await self._lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self._lock.release()
        self._change_event.set()