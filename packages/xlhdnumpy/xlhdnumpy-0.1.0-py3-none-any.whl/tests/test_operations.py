import unittest
from xlhdnumpy import array, add, subtract, multiply, divide, sum, mean

class TestOperations(unittest.TestCase):
    
    def test_add(self):
        arr1 = array([1, 2, 3])
        arr2 = array([4, 5, 6])
        result = add(arr1, arr2)
        self.assertEqual(result.data, [5, 7, 9])
    
    def test_subtract(self):
        arr1 = array([10, 8, 6])
        arr2 = array([4, 5, 2])
        result = subtract(arr1, arr2)
        self.assertEqual(result.data, [6, 3, 4])
    
    def test_multiply(self):
        arr1 = array([2, 3, 4])
        arr2 = array([5, 6, 7])
        result = multiply(arr1, arr2)
        self.assertEqual(result.data, [10, 18, 28])
    
    def test_divide(self):
        arr1 = array([10, 8, 6])
        arr2 = array([2, 4, 3])
        result = divide(arr1, arr2)
        self.assertEqual(result.data, [5.0, 2.0, 2.0])
    
    def test_sum(self):
        arr = array([1, 2, 3, 4])
        self.assertEqual(sum(arr), 10)
    
    def test_mean(self):
        arr = array([1, 2, 3, 4])
        self.assertEqual(mean(arr), 2.5)
    
    def test_shape_mismatch(self):
        arr1 = array([1, 2])
        arr2 = array([3, 4, 5])
        with self.assertRaises(ValueError):
            add(arr1, arr2)

if __name__ == "__main__":
    unittest.main()
