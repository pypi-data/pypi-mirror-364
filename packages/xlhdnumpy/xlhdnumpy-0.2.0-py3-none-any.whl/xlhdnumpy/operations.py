from .array import MyArray
import math

def add(arr1, arr2):
    """两个数组相加"""
    if not isinstance(arr1, MyArray) or not isinstance(arr2, MyArray):
        raise TypeError("操作数必须是MyArray实例")
    
    if arr1.shape != arr2.shape:
        raise ValueError("数组形状必须相同")
    
    result_data = [a + b for a, b in zip(arr1.data, arr2.data)]
    return MyArray(result_data)

def subtract(arr1, arr2):
    """两个数组相减"""
    if not isinstance(arr1, MyArray) or not isinstance(arr2, MyArray):
        raise TypeError("操作数必须是MyArray实例")
    
    if arr1.shape != arr2.shape:
        raise ValueError("数组形状必须相同")
    
    result_data = [a - b for a, b in zip(arr1.data, arr2.data)]
    return MyArray(result_data)

def multiply(arr1, arr2):
    """两个数组相乘"""
    if not isinstance(arr1, MyArray) or not isinstance(arr2, MyArray):
        raise TypeError("操作数必须是MyArray实例")
    
    if arr1.shape != arr2.shape:
        raise ValueError("数组形状必须相同")
    
    result_data = [a * b for a, b in zip(arr1.data, arr2.data)]
    return MyArray(result_data)

def divide(arr1, arr2):
    """两个数组相除"""
    if not isinstance(arr1, MyArray) or not isinstance(arr2, MyArray):
        raise TypeError("操作数必须是MyArray实例")
    
    if arr1.shape != arr2.shape:
        raise ValueError("数组形状必须相同")
    
    result_data = [a / b for a, b in zip(arr1.data, arr2.data)]
    return MyArray(result_data)

def sum(arr):
    """计算数组元素的总和"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    return sum(arr.data)

def mean(arr):
    """计算数组元素的平均值"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    if arr.size == 0:
        raise ValueError("空数组无法计算平均值")
    
    return sum(arr.data) / arr.size

def min(arr):
    """计算数组的最小值"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    if arr.size == 0:
        raise ValueError("空数组无法计算最小值")
    
    return min(arr.data)

def max(arr):
    """计算数组的最大值"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    if arr.size == 0:
        raise ValueError("空数组无法计算最大值")
    
    return max(arr.data)

def unique(arr):
    """返回数组中的唯一值（去重并排序）"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    if arr.size == 0:
        return MyArray([])
    
    unique_data = sorted(set(arr.data))
    return MyArray(unique_data, dtype=arr.dtype)

def median(arr):
    """计算数组的中位数"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    if arr.size == 0:
        raise ValueError("空数组无法计算中位数")
    
    sorted_data = sorted(arr.data)
    n = len(sorted_data)
    mid = n // 2
    
    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2.0
    else:
        return sorted_data[mid]