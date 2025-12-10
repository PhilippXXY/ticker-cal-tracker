from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    username: str
    email: str
    password_hash: str
    created_at: datetime = None
    id: Optional[int] = None