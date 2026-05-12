"""
Version information for ComfyUI-UnlimitAI
"""

__version__ = "1.2.0"
__author__ = "ComfyUI-UnlimitAI Team"
__email__ = "contact@example.com"
__license__ = "MIT"
__url__ = "https://github.com/your-repo/ComfyUI-UnlimitAI"

VERSION = tuple(map(int, __version__.split('.')))
VERSION_STR = __version__

# Version history
VERSION_HISTORY = {
    "1.0.0": "2025-01-XX - Initial release",
}

def get_version():
    """Get the current version string."""
    return __version__

def get_version_info():
    """Get detailed version information."""
    return {
        "version": __version__,
        "author": __author__,
        "license": __license__,
    }
