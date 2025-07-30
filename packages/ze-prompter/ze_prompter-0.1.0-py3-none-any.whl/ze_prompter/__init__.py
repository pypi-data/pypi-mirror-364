from .core import PromptManager, ModelManager, AuthManager
from .models import init_db
from .manager import get_manager, Manager, reset_manager

__version__ = "0.1.0"
__author__ = "Olsi Hoxha"
__email__ = "olsihoxha824@gmail.com"
__description__ = "A library for managing prompt templates with versioning and AI models"

__all__ = [
    # New simplified API
    "get_manager", "Manager", "reset_manager",
    # Direct access (for advanced users)
    "PromptManager", "ModelManager", "AuthManager", "init_db"
]