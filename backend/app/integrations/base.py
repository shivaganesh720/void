from abc import ABC, abstractmethod
from typing import Any

class BaseIntegration(ABC):
    """Abstract base class for third-party integrations (GitHub, Notion, etc.)."""
    
    @abstractmethod
    def authenticate(self, credentials: dict) -> bool:
        """Authenticate with the integration provider."""
        pass
        
    @abstractmethod
    def execute_action(self, action_name: str, payload: dict) -> dict[str, Any]:
        """Execute a predefined action for this integration."""
        pass
        
    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        """Check connection health."""
        pass
