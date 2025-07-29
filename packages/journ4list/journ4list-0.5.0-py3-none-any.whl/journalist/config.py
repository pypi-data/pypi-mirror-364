"""
Global configuration for journalist package.
"""

import os

class JournalistConfig:
    """Centralized configuration for Journalist class."""
    
    # Environment detection
    IS_LOCAL = os.getenv('ENVIRONMENT', 'local') == 'local'
    
    # Default values - environment dependent
    if IS_LOCAL:
        DEFAULT_BASE_WORKSPACE_PATH = ".journalist_workspace"
    else:
        DEFAULT_BASE_WORKSPACE_PATH = "/tmp/.journalist_workspace"
    
    def __init__(self):
        """Initialize configuration with defaults."""
        self.base_workspace_path = self.DEFAULT_BASE_WORKSPACE_PATH
    
    @classmethod
    def get_base_workspace_path(cls) -> str:
        """Get base workspace path."""
        return cls.DEFAULT_BASE_WORKSPACE_PATH
