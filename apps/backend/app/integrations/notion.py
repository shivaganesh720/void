from typing import Any
from app.integrations.base import BaseIntegration

class NotionIntegration(BaseIntegration):
    """Notion Integration Client with local mock fallback for development."""
    
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self.is_authenticated = False
        
    def authenticate(self, credentials: dict) -> bool:
        if self.mock_mode:
            self.is_authenticated = True
            return True
        return False
        
    def execute_action(self, action_name: str, payload: dict) -> dict[str, Any]:
        if not self.is_authenticated:
            raise PermissionError("Not authenticated with Notion")
            
        if self.mock_mode:
            if action_name == "create_page":
                return {"status": "success", "page_id": "mock-page-id-123", "url": "https://notion.so/mock"}
            elif action_name == "search_pages":
                return {"status": "success", "results": [{"title": "Mock Notes", "id": "123"}]}
                
        raise NotImplementedError(f"Action {action_name} not implemented for production mode.")

    def health_check(self) -> dict[str, Any]:
        return {"service": "notion", "status": "healthy" if self.mock_mode else "unconfigured"}
