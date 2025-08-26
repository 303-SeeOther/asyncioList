# 重生之asyncioList：异步列表的救赎

前世的我，在异步编程的泥潭里反复挣扎——多协程操作列表时的race condition（竞态条件）像幽灵一样挥之不去，手动加锁时的繁琐代码让逻辑支离破碎，想在异步迭代里遍历列表却总被中途修改的元素搞得晕头转向……直到某次线上事故因为列表并发操作崩溃，我才痛悟：异步环境下的列表操作，真的需要一个简单却靠谱的解决方案。

重生归来，带着对异步编程痛点的深刻理解，我写下了`asyncioList`——一个简单到几乎不用学，却能解决异步列表操作所有麻烦的工具。


## 它为什么值得你用？

`asyncioList`没什么惊天动地的黑科技，却把异步列表该有的样子做到了极致：

- **简单得像在用普通列表**：`append`、`pop`、`get`、`index`……所有方法都和原生列表一一对应，只是加了`await`关键字，上手零成本。
- **天生抗并发**：内置`asyncio.Lock`，不管多少协程同时操作，都能保证数据安全，不用再自己手动加锁解锁。
- **异步场景全适配**：支持异步迭代（`async for`）、等待列表变化（`wait_for_change`）、上下文管理器批量操作，完美融入你的异步代码流。
- **轻得像一阵风**：只依赖Python标准库，安装即用，不会给你的项目增加任何额外负担。


## 快速上手：重生后的第一次操作

### 安装

```bash
# 从源码安装
pip install git+https://github.com/303-SeeOther/asyncioList.git
# 或者从pypi安装
pip install asyncioList
```

### 基础用法（~~1分钟就能学会~~你已经会了）

```python
import asyncio
from asyncioList.AsyncioList import AsyncioList

async def main():
    # 创建列表（和普通列表一样简单）
    my_list = AsyncioList([1, 2, 3])
    
    # 加个元素（加个await就好）
    await my_list.append(4)
    print(await my_list.get(3))  # 输出：4
    
    # 删个元素
    await my_list.pop(0)
    print(await my_list.length())  # 输出：3
    
    # 查个索引
    print(await my_list.index(3))  # 输出：1

asyncio.run(main())
```


## 进阶玩法：那些前世没享过的便利

### 异步迭代，遍历不慌

```python
async def iterate_example():
    fruits = AsyncioList(['apple', 'banana', 'cherry'])
    async for fruit in fruits:  # 直接用async for遍历
        print(fruit)
```

### 等待列表变化，实时响应

```python
async def watch_example():
    my_list = AsyncioList()
    
    # 一个协程修改列表
    async def add_items():
        await asyncio.sleep(1)
        await my_list.append("重生了！")
    
    # 另一个协程等待变化
    async def watcher():
        await my_list.wait_for_change()  # 等列表变了再继续
        print(await my_list.get(0))  # 输出：重生了！
    
    await asyncio.gather(add_items(), watcher())
```

### 上下文管理器，批量操作更高效

```python
async def context_example():
    async with AsyncioList([1, 2, 3]) as ctx_list:
        # 批量操作直接改内部列表，省掉多次加锁开销
        ctx_list._items.extend([4, 5, 6])
        ctx_list._items.reverse()
    print(await ctx_list.slice(0, 6))  # 输出：[6, 5, 4, 3, 2, 1]
```

### 生产者消费者模型：并发协作的正确姿势

前世手写生产者消费者时，总在列表操作上栽跟头——要么漏数据，要么重复处理，加锁逻辑稍不注意就死锁。有了`asyncioList`，多协程协作变得像呼吸一样自然：

```python
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
        *[producer(f"P{i+1}", queue, 5, producers_done) for i in range(3)],
        *[consumer(f"C{i+1}", queue, producers_done) for i in range(2)]
    )

asyncio.run(main())
```

这个示例里，`asyncioList`默默搞定了所有锁管理：生产者并发添加不冲突，消费者安全读取不重复，批量操作还能通过上下文管理器减少锁开销——终于不用再为“谁先加锁谁后解锁”掉头发了。
详细实例请看[example](example)目录

## 结尾(凑字数用的)

`asyncioList`真的很简单，只是个小工具，但是在异步编程中操作列表时，总会遇到一些问题，比如race condition（竞态条件）、死锁等。这些问题都可以通过`asyncioList`来避免，避免了手动加锁解锁的繁琐代码，同时也避免了race condition的问题。
发到pypi上~~只是方便自己拉~~是为了帮助大家节省一点时间，少掉几根头发。
如果你的异步代码里也需要操作列表，欢迎使用`asyncioList`。

↑↑以上内容均由豆包生成