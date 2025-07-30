import unittest
from rhit.vilo import vilo

class TestVilo(unittest.TestCase):
    def test_vilo_function(self):
        # Add test cases for the vilo function here
        self.assertEqual(vilo(2), 4)  # Example test case
        self.assertEqual(vilo(-1), 1)  # Example test case

if __name__ == '__main__':
    unittest.main()