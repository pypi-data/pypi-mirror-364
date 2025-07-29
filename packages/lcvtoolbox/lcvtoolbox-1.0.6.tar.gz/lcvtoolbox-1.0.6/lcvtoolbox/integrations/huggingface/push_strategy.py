from enum import Enum


class PushStrategy(Enum):
    """Defines the push strategy for datasets after operations."""
    
    ALWAYS = "always"  # Always push to remote after operations
    NEVER = "never"  # Never push to remote (work locally only)
    
    @classmethod
    def from_string(cls, value: str) -> "PushStrategy":
        """Convert string to PushStrategy enum."""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(
                f"Invalid push strategy: {value}. "
                f"Valid options are: {', '.join([s.value for s in cls])}"
            )
