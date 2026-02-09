from enum import Enum

class SessionStatus(Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    FINISHED = "finished"
    ABORTED = "aborted"