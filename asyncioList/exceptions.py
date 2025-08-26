"""asyncioList异常模块

包含asyncioList包的所有自定义异常类。

作者: 303_SeeOther
邮箱: l.z.cheng.1106@gmail.com
版本: 1.0
"""
class AsyncioListError(Exception):
    """AsyncioList操作的基础异常类"""
    pass


class IndexOutOfBoundsError(AsyncioListError):
    """当访问超出列表范围的索引时引发"""
    pass