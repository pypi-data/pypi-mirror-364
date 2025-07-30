"""
Matcha AI - A placeholder package for matcha-ai
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

def hello():
    """
    A simple hello function for testing the package.
    
    Returns:
        str: A greeting message
    """
    return "Hello from Matcha AI! 🍵"

def get_version():
    """
    Get the current version of the package.
    
    Returns:
        str: The version string
    """
    return __version__

# Make functions available at package level
__all__ = ["hello", "get_version"]
