from enum import Enum


class SyncStrategy(Enum):
    """Defines the synchronization strategy for datasets."""
    
    ALWAYS = "always"  # Always download from remote
    IF_CHANGED = "if-changed"  # Only download if remote has changes
    NEVER = "never"  # Never download if local exists (but download if local doesn't exist)
    
    @classmethod
    def from_string(cls, value: str) -> "SyncStrategy":
        """Convert string to SyncStrategy enum."""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(
                f"Invalid sync strategy: {value}. "
                f"Valid options are: {', '.join([s.value for s in cls])}"
            )
