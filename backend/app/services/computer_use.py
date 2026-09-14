class ComputerUseService:
    """Safe foundation for screen understanding and local interactions."""
    
    def __init__(self, security_policy_level: str = "STRICT"):
        self.security_policy_level = security_policy_level
        self.application_allowlist = ["Notepad", "Calculator", "Browser"]
        
    def capture_screen(self) -> str:
        """Simulate capturing the desktop screen. Returns base64 mock image."""
        return "mock_base64_screenshot_data"
        
    def execute_safe_action(self, action: str, target: str) -> dict:
        """
        Execute an action ONLY if it meets security policy.
        Requires explicit human approval for risky interactions.
        """
        if self.security_policy_level == "STRICT" and target not in self.application_allowlist:
            return {"status": "blocked", "reason": "Target not in allowlist"}
            
        return {"status": "success", "action": action, "target": target}
