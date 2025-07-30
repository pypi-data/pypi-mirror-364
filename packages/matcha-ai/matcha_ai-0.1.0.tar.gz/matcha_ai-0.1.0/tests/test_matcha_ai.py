"""
Tests for matcha_ai package
"""

import unittest
import matcha_ai


class TestMatchaAI(unittest.TestCase):
    """Test cases for matcha_ai package"""
    
    def test_hello(self):
        """Test the hello function"""
        result = matcha_ai.hello()
        self.assertIsInstance(result, str)
        self.assertIn("Hello", result)
        self.assertIn("Matcha AI", result)
    
    def test_get_version(self):
        """Test the get_version function"""
        version = matcha_ai.get_version()
        self.assertIsInstance(version, str)
        self.assertEqual(version, "0.1.0")
    
    def test_version_attribute(self):
        """Test the __version__ attribute"""
        self.assertEqual(matcha_ai.__version__, "0.1.0")


if __name__ == "__main__":
    unittest.main()
