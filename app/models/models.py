from pydantic import BaseModel
from typing import Optional

class LoginData(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False

class SirenData(BaseModel):
    current: float
    mode: int
    over: bool = False
    testing: bool = False
    barcode: Optional[str] = None
    operator: Optional[str] = None
    limit: Optional[float] = 50.5
    elapsed: Optional[float] = 0

class UserResponse(BaseModel):
    username: str
    is_admin: bool

# ==================== مدل‌های اعلان‌ها (جدید) ====================

class NotificationCreate(BaseModel):
    receiver: str  # یا "ALL" برای همگانی
    title: str
    message: str
    notification_type: Optional[str] = "admin_message"

class NotificationResponse(BaseModel):
    id: int
    sender: str
    receiver: str
    title: str
    message: str
    is_read: bool
    is_broadcast: bool
    notification_type: str
    created_at: str