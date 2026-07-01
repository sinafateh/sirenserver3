import hashlib
import secrets
from app.database.database import get_user_with_password, create_session, delete_session, get_session_user

def hash_password(password: str) -> str:
    """هش کردن رمز عبور"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """تأیید رمز عبور"""
    return hash_password(password) == password_hash

def authenticate_user(username: str, password: str):
    """احراز هویت کاربر"""
    user = get_user_with_password(username)
    if not user:
        return None
    
    if not verify_password(password, user["password_hash"]):
        return None
    
    return {"username": user["username"], "is_admin": user["is_admin"]}

def create_user_session(username: str) -> str:
    """ایجاد سشن برای کاربر"""
    session_id = secrets.token_urlsafe(32)
    create_session(session_id, username)
    return session_id

def get_user_from_session(session_id: str):
    """دریافت کاربر از سشن"""
    return get_session_user(session_id)

def remove_session(session_id: str):
    """حذف سشن"""
    delete_session(session_id)