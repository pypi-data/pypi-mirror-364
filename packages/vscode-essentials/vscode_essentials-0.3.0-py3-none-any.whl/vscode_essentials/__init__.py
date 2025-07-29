"""
vscode-essentials: Essential utilities for VS Code development
"""

import os

__version__ = "0.3.0"
__author__ = "SAI"
__email__ = "me@steveimm.id"

# You can add your main functions or classes here
def hello_world():
    """Simple hello world function for testing."""
    return "Hello from vscode-essentials!"

def get_vsix_directory():
    """Get the path to the bundled VSIX files."""
    return os.path.join(os.path.dirname(__file__), 'vsix')

def list_vsix_files():
    """List all available VSIX files."""
    vsix_dir = get_vsix_directory()
    if os.path.exists(vsix_dir):
        return [f for f in os.listdir(vsix_dir) if f.endswith('.vsix')]
    return []

def get_vsix_path(filename):
    """Get the full path to a specific VSIX file."""
    vsix_dir = get_vsix_directory()
    return os.path.join(vsix_dir, filename)