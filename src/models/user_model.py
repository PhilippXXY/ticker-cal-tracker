from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class User:
    email: str
    created_at: datetime
    