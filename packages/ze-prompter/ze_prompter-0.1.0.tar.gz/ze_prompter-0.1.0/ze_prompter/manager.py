"""
ZePrompter Manager - Unified interface for prompt and model management
"""
from typing import Optional
from sqlalchemy.orm import Session
from .models.database import SessionLocal, init_db, get_db
from .core.prompt_manager import PromptManager
from .core.model_manager import ModelManager


class Manager:
    """
    Unified manager for ZePrompter that provides easy access to prompt and model management.
    
    This is the main interface you should use to interact with ZePrompter.
    It automatically handles database initialization and provides access to
    both prompt_manager and model_manager instances.
    
    Example:
        from ze_prompter import get_manager
        
        manager = get_manager()
        
        # Create a new prompt template
        template = manager.prompt_manager.create_prompt_template(
            name="greeting",
            content="Hello {name}!"
        )
        
        # Create a new model
        model = manager.model_manager.create_model(
            name="gpt-4",
            description="OpenAI GPT-4 model"
        )
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the Manager.
        
        Args:
            db_session: Optional database session. If not provided, a new session will be created.
        """
        self._db_session = db_session
        self._prompt_manager = None
        self._model_manager = None
        self._db_initialized = False
    
    @property
    def db(self) -> Session:
        """Get the database session, creating one if needed."""
        if self._db_session is None:
            self._ensure_db_initialized()
            self._db_session = SessionLocal()
        return self._db_session
    
    @property
    def prompt_manager(self) -> PromptManager:
        """Get the PromptManager instance."""
        if self._prompt_manager is None:
            self._prompt_manager = PromptManager(self.db)
        return self._prompt_manager
    
    @property
    def model_manager(self) -> ModelManager:
        """Get the ModelManager instance."""
        if self._model_manager is None:
            self._model_manager = ModelManager(self.db)
        return self._model_manager
    
    def _ensure_db_initialized(self):
        """Ensure the database is initialized."""
        if not self._db_initialized:
            init_db()
            self._db_initialized = True
    
    def close(self):
        """Close the database session if it was created by this manager."""
        if self._db_session:
            self._db_session.close()
            self._db_session = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global manager instance
_manager_instance: Optional[Manager] = None


def get_manager(db_session: Optional[Session] = None) -> Manager:
    """
    Get a Manager instance.
    
    This is the main entry point for ZePrompter. It returns a Manager instance
    that provides access to prompt_manager and model_manager.
    
    Args:
        db_session: Optional database session. If not provided, a new session will be created.
    
    Returns:
        Manager: A Manager instance with prompt_manager and model_manager properties.
        
    Example:
        from ze_prompter import get_manager
        
        # Get manager instance
        manager = get_manager()
        
        # Use prompt manager
        template = manager.prompt_manager.create_prompt_template(
            name="greeting",
            content="Hello {name}!"
        )
        
        # Use model manager  
        model = manager.model_manager.create_model(
            name="gpt-4",
            description="OpenAI GPT-4 model"
        )
    """
    global _manager_instance
    
    if db_session is not None:
        # If a specific session is provided, always create a new manager
        return Manager(db_session)
    
    if _manager_instance is None:
        _manager_instance = Manager()
    
    return _manager_instance


def reset_manager():
    """Reset the global manager instance. Useful for testing."""
    global _manager_instance
    if _manager_instance:
        _manager_instance.close()
    _manager_instance = None
