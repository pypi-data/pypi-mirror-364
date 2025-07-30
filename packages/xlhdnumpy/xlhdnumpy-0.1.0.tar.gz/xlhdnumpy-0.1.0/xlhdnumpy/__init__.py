from .array import MyArray
from .operations import add, subtract, multiply, divide, sum, mean

__version__ = "0.1.0"

# 提供类似numpy的接口
def array(data, dtype=None):
    """创建一个新的MyArray实例"""
    return MyArray(data, dtype)

# 导出公共API
__all__ = ["MyArray", "array", "add", "subtract", "multiply", "divide", "sum", "mean", "__version__"]
