import numbers

class MyArray:
    """简易的数组类，模拟numpy的ndarray"""
    
    def __init__(self, data, dtype=None):
        """
        初始化数组
        
        参数:
            data: 可迭代对象，用于创建数组
            dtype: 数据类型，默认为None（自动推断）
        """
        # 转换数据为列表
        self.data = list(data)
        
        # 检查所有元素是否为数字
        for item in self.data:
            if not isinstance(item, numbers.Number):
                raise TypeError("数组元素必须是数字")
        
        # 推断数据类型
        if dtype is None:
            if all(isinstance(x, int) for x in self.data):
                self.dtype = int
            else:
                self.dtype = float
        else:
            self.dtype = dtype
            # 转换数据为指定类型
            self.data = [dtype(x) for x in self.data]
        
        self.shape = (len(self.data),)
        self.size = len(self.data)
    
    def __repr__(self):
        return f"MyArray({self.data}, dtype={self.dtype.__name__})"
    
    def __len__(self):
        return self.size
    
    def __getitem__(self, index):
        return self.data[index]
    
    def __setitem__(self, index, value):
        # 确保设置的值与数组数据类型一致
        self.data[index] = self.dtype(value)
