import asyncio
import random
from asyncioList.AsyncioList import AsyncioList


async def producer(name: str, queue: AsyncioList, max_items: int, done_event: asyncio.Event):
    """生产者：生成数据并添加到列表（混合单条/批量操作）"""
    for i in range(max_items):
        await asyncio.sleep(random.uniform(0.1, 0.5))  # 模拟生产耗时
        item = f"[{name}]产品_{i}_{random.randint(1000, 9999)}"

        if i % 3 != 0:  # 普通添加
            await queue.append(item)
            print(f"生产者{name} 添加: {item} | 当前长度: {await queue.length()}")
        else:  # 批量添加（上下文管理器高效操作）
            batch = [item, f"[{name}]批量产品_{i}_1", f"[{name}]批量产品_{i}_2"]
            async with queue:
                queue._items.extend(batch)
            print(f"生产者{name} 批量添加{len(batch)}个元素")
    done_event.set()  # 标记当前生产者完成


async def consumer(name: str, queue: AsyncioList, producers_done: asyncio.Event):
    """消费者：等待列表变化并处理元素"""
    while True:
        # 等待列表变化（超时1秒防阻塞）
        changed = await queue.wait_for_change(timeout=1.0)

        # 退出条件：所有生产者完成且队列空
        if producers_done.is_set() and await queue.is_empty():
            print(f"消费者{name} 任务完成，退出")
            break

        if changed or not await queue.is_empty():
            # 处理所有可用元素
            while not await queue.is_empty():
                item = await queue.pop(0)  # 取出首个元素
                await asyncio.sleep(random.uniform(0.2, 0.6))  # 模拟处理耗时
                print(f"消费者{name} 处理完成: {item} | 剩余: {await queue.length()}")


# 运行示例
async def main():
    queue = AsyncioList()
    producers_done = asyncio.Event()

    # 3个生产者+2个消费者并发协作
    await asyncio.gather(
        *[producer(f"P{i + 1}", queue, 5, producers_done) for i in range(3)],
        *[consumer(f"C{i + 1}", queue, producers_done) for i in range(2)]
    )


asyncio.run(main())