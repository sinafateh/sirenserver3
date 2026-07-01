from fastapi import APIRouter, Request, HTTPException, Response, Header
from fastapi.responses import JSONResponse, RedirectResponse
from app.models.models import LoginData
from app.services.auth_service import (
    authenticate_user, 
    create_user_session, 
    get_user_from_session, 
    remove_session
)

router = APIRouter()

# ==================== لاگین (بدون کوکی) ====================
@router.post("/api/login")
async def login(data: LoginData):
    """ورود کاربر - Session ID در پاسخ JSON برگردانده میشه"""
    user = authenticate_user(data.username, data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # ایجاد Session
    session_id = create_user_session(data.username)
    
    return JSONResponse({
        "status": "success",
        "username": user["username"],
        "is_admin": user["is_admin"],
        "session_id": session_id  # کلید اصلی: برگردوندن Session ID
    })

# ==================== خروج ====================
@router.post("/api/logout")
async def logout(session_id: str = Header(None)):
    """خروج کاربر با Session ID از Header"""
    if session_id:
        remove_session(session_id)
    return JSONResponse({"status": "success"})

# ==================== دریافت اطلاعات کاربر فعلی ====================
@router.get("/api/me")
async def get_me(session_id: str = Header(None)):
    """دریافت اطلاعات کاربر از Session ID"""
    if not session_id:
        return JSONResponse({"authenticated": False})
    
    user = get_user_from_session(session_id)
    if not user:
        return JSONResponse({"authenticated": False})
    
    return JSONResponse({
        "authenticated": True,
        "username": user["username"],
        "is_admin": user["is_admin"]
    })

# ==================== تابع کمکی برای دریافت کاربر از Header ====================
def get_current_user_from_header(session_id: str = Header(None)):
    """دریافت کاربر فعلی از Header"""
    if not session_id:
        return None
    return get_user_from_session(session_id)
