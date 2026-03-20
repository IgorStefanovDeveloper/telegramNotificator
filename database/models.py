"""Event and user models."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Recurrence types
RECURRENCE_NONE = "none"
RECURRENCE_MONTHLY = "monthly"   # e.g. 19th of every month
RECURRENCE_WEEKLY = "weekly"     # e.g. every Monday


@dataclass
class User:
    id: int
    telegram_id: int
    language: str
    timezone: str
    created_at: datetime


@dataclass
class Event:
    id: int
    user_id: int
    title: str
    description: Optional[str]
    event_datetime: datetime
    timezone: str
    recurrence_type: str
    recurrence_value: Optional[str]  # day of month for monthly, weekday for weekly
    is_completed: bool
    created_at: datetime
    notified_at: Optional[datetime] = None
    is_cancelled: bool = False
    cancelled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    nudge_count: int = 0
