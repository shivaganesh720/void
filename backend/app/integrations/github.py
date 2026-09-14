from typing import Any
from app.integrations.base import BaseIntegration

class GitHubIntegration(BaseIntegration):
    """GitHub Integration Client with local mock fallback for development."""
    
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self.is_authenticated = False
        
    def authenticate(self, credentials: dict) -> bool:
        if self.mock_mode:
            self.is_authenticated = True
            return True
        # Production OAuth logic here
        return False
        
    def execute_action(self, action_name: str, payload: dict) -> dict[str, Any]:
        if not self.is_authenticated:
            raise PermissionError("Not authenticated with GitHub")
            
        if self.mock_mode:
            # Local fallback / dev mock
            if action_name == "list_issues":
                return {"status": "success", "issues": [{"id": 1, "title": "Mock Issue", "state": "open"}]}
            elif action_name == "create_pr":
                return {"status": "success", "url": "https://github.com/mock/mock/pull/1"}
                
        # Production execution logic here
        raise NotImplementedError(f"Action {action_name} not implemented for production mode.")

    def health_check(self) -> dict[str, Any]:
        return {"service": "github", "status": "healthy" if self.mock_mode else "unconfigured"}
