from typing import Any, Dict, Optional
class TodoistException(Exception):
    def __init__(
        self, 
        message: str, 
        code: Optional[str | int] = None, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        # Call the base Exception's __init__ with the main message.
        # This ensures `str(e)` works out of the box.
        super().__init__(message)
        
        self.message: str = message
        self.code: Optional[str | int] = code
        self.details: Dict[str, Any] = details or {}

    def __str__(self) -> str:
        """Custom string representation for logging."""
        base_str: str = f"[{self.code}] {self.message}" if self.code else self.message
        
        if self.details:
            details_str: str = ", ".join(f"{k}={v!r}" for k, v in self.details.items())
            return f"{base_str} (Details: {details_str})"
            
        return base_str
    def name(self) -> str:
        return self.__class__.__name__
