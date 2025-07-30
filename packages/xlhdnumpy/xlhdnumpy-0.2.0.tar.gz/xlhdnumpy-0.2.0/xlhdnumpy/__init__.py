from .array import MyArray
from .operations import add, subtract, multiply, divide, sum, mean, min, max, unique, median

__version__ = "0.2.0"  # 更新版本号

# 提供类似numpy的接口
def array(data, dtype=None):
    """创建一个新的MyArray实例"""
    return MyArray(data, dtype)

# 导出公共API（添加新增函数）
__all__ = [
    "MyArray", "array", "add", "subtract", "multiply", "divide", 
    "sum", "mean", "min", "max", "unique", "median", "__version__"
]