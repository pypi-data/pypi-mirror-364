import unittest
from xlhdnumpy import array, MyArray

class TestMyArray(unittest.TestCase):
    
    def test_create_array(self):
        arr = array([1, 2, 3, 4])
        self.assertIsInstance(arr, MyArray)
        self.assertEqual(arr.shape, (4,))
        self.assertEqual(arr.size, 4)
        self.assertEqual(arr.dtype, int)
    
    def test_create_float_array(self):
        arr = array([1.5, 2.0, 3, 4])
        self.assertEqual(arr.dtype, float)
    
    def test_specify_dtype(self):
        arr = array([1, 2, 3], dtype=float)
        self.assertEqual(arr.dtype, float)
        self.assertEqual(arr.data, [1.0, 2.0, 3.0])
    
    def test_invalid_data(self):
        with self.assertRaises(TypeError):
            array([1, "2", 3])
    
    def test_indexing(self):
        arr = array([10, 20, 30])
        self.assertEqual(arr[0], 10)
        self.assertEqual(arr[2], 30)
        
        arr[1] = 25
        self.assertEqual(arr[1], 25)

if __name__ == "__main__":
    unittest.main()
