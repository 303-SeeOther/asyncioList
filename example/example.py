import asyncio
from asyncioList.AsyncioList import AsyncioList


# ============================ 基础用法示例 ============================
async def basic_usage_example():
    print("===== 基础用法示例 ======")

    # 1. 创建AsyncioList实例
    # 可以不提供初始列表，或提供一个初始列表
    empty_list = AsyncioList()
    numbers = AsyncioList([1, 2, 3, 4, 5])
    print(f"初始列表: {numbers}")  # 输出: AsyncioList(items=[1, 2, 3, 4, 5])

    # 2. 添加元素
    # append: 添加单个元素到末尾
    await numbers.append(6)
    print(f"添加元素6后: {numbers}")  # 输出: AsyncioList(items=[1, 2, 3, 4, 5, 6])

    # extend: 添加多个元素到末尾
    await numbers.extend([7, 8, 9])
    print(f"添加多个元素后: {numbers}")  # 输出: AsyncioList(items=[1, 2, 3, 4, 5, 6, 7, 8, 9])

    # insert: 在指定位置插入元素
    await numbers.insert(0, 0)  # 在索引0处插入0
    print(f"插入元素0后: {numbers}")  # 输出: AsyncioList(items=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    # 3. 访问元素
    # get: 获取指定索引的元素
    third_element = await numbers.get(2)
    print(f"索引2处的元素: {third_element}")  # 输出: 2

    # index: 查找元素的索引
    index_of_5 = await numbers.index(5)
    print(f"元素5的索引: {index_of_5}")  # 输出: 5

    # 查找元素5从索引5开始到索引8结束的第一个匹配项
    index_of_5_start_5 = await numbers.index(5, start=5, end=8)
    print(f"元素5从索引5开始的第一个匹配项索引: {index_of_5_start_5}")  # 输出: 5

    # count: 统计元素出现次数
    count_of_3 = await numbers.count(3)
    print(f"元素3出现次数: {count_of_3}")  # 输出: 1

    # contains: 检查元素是否存在
    has_10 = await numbers.contains(10)
    print(f"列表是否包含10: {has_10}")  # 输出: False

    # length: 获取列表长度
    list_length = await numbers.length()
    print(f"列表长度: {list_length}")  # 输出: 10

    # is_empty: 检查列表是否为空
    is_empty = await empty_list.is_empty()
    print(f"空列表是否为空: {is_empty}")  # 输出: True

    # 4. 删除元素
    # remove: 删除第一个出现的指定元素
    await numbers.remove(0)  # 删除元素0
    print(f"删除元素0后: {numbers}")  # 输出: AsyncioList(items=[1, 2, 3, 4, 5, 6, 7, 8, 9])

    # pop: 删除并返回指定索引的元素
    last_element = await numbers.pop()  # 默认删除最后一个元素
    print(f"删除的最后一个元素: {last_element}")  # 输出: 9
    print(f"pop后列表: {numbers}")  # 输出: AsyncioList(items=[1, 2, 3, 4, 5, 6, 7, 8])

    # delete_all: 删除所有指定元素
    # 先添加几个重复元素用于演示
    await numbers.append(2)
    await numbers.append(2)
    print(f"添加重复元素2后: {numbers}")  # 输出: AsyncioList(items=[1, 2, 3, 4, 5, 6, 7, 8, 2, 2])
    await numbers.delete_all(2)
    print(f"删除所有元素2后: {numbers}")  # 输出: AsyncioList(items=[1, 3, 4, 5, 6, 7, 8])

    # clear: 清空列表
    await empty_list.clear()
    print(f"清空空列表后是否为空: {await empty_list.is_empty()}")  # 输出: True


# ============================ 高级用法示例 ============================
async def advanced_usage_example():
    print("\n===== 高级用法示例 ======")

    # 1. 异步迭代器
    fruits = AsyncioList(['apple', 'banana', 'cherry'])
    print("异步迭代列表元素:")
    async for fruit in fruits:
        print(f"- {fruit}")

    # 2. 等待列表变化
    # 创建一个协程函数用于修改列表
    async def modify_list(list_obj: AsyncioList):
        await asyncio.sleep(1)  # 模拟一些异步操作
        await list_obj.append('date')
        await asyncio.sleep(1)
        await list_obj.append('elderberry')

    # 创建一个协程函数用于等待变化
    async def watch_list(list_obj: AsyncioList):
        print("开始监视列表变化...")
        while True:
            # 等待列表变化，超时时间3秒
            changed = await list_obj.wait_for_change(timeout=3)
            if changed:
                print(f"列表发生变化: {list_obj}")
            else:
                print("等待超时，列表未发生变化")
                break

    # 同时运行修改和监视协程
    print("\n演示等待列表变化:")
    list_watcher = AsyncioList(['apple', 'banana'])
    await asyncio.gather(
        modify_list(list_watcher),
        watch_list(list_watcher)
    )

    # 3. 使用上下文管理器
    print("\n使用上下文管理器批量操作:")
    async with AsyncioList([1, 2, 3]) as ctx_list:
        # 在上下文管理器中可以直接访问_items属性进行批量操作
        # 注意: 这会绕过常规的异步方法，应谨慎使用
        ctx_list._items.extend([4, 5, 6])
        ctx_list._items.reverse()
    print(f"上下文管理器操作后的列表: {ctx_list}")  # 输出: AsyncioList(items=[6, 5, 4, 3, 2, 1])

    # 4. 链式调用
    print("\n链式调用示例:")
    chained_list = AsyncioList()
    # 想多了，异步方法的链式调用在Python中无法直接实现
    await chained_list.append(1)
    await chained_list.append(2)
    await chained_list.extend([3, 4])
    await chained_list.insert(0, 0)
    await chained_list.reverse()
    result = chained_list
    print(f"链式调用结果: {result}")  # 输出: AsyncioList(items=[4, 3, 2, 1, 0])

    # 5. 并发操作安全演示
    print("\n并发操作安全演示:")
    concurrent_list = AsyncioList()

    # 创建10个协程同时向列表添加元素
    async def add_item(index):
        await concurrent_list.append(f'item_{index}')

    # 并发执行10个添加操作
    await asyncio.gather(*[add_item(i) for i in range(10)])
    print(f"并发添加后的列表长度: {await concurrent_list.length()}")  # 输出: 10
    print(f"并发添加的元素: {concurrent_list}")


# 运行示例
if __name__ == "__main__":
    asyncio.run(basic_usage_example())
    asyncio.run(advanced_usage_example())
