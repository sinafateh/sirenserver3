from fastapi import APIRouter, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from app.models.models import UserCreate
from app.services.auth_service import get_user_from_session, hash_password
from app.database.database import get_all_users, get_user_by_username, add_user, delete_user

router = APIRouter()

def require_admin(session_id: str = Header(None)):
    """بررسی اینکه کاربر ادمین باشد"""
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_user_from_session(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.get("/api/users")
async def get_users(current_user = Depends(require_admin)):
    """دریافت لیست کاربران"""
    return JSONResponse(get_all_users())

@router.post("/api/users")
async def add_new_user(user: UserCreate, current_user = Depends(require_admin)):
    """افزودن کاربر جدید"""
    if user.username == "sina":
        raise HTTPException(status_code=400, detail="Username 'sina' is reserved")
    
    password_hash = hash_password(user.password)
    if add_user(user.username, password_hash, user.is_admin):
        return JSONResponse({"status": "success", "message": "User added"})
    else:
        raise HTTPException(status_code=400, detail="Username already exists")

@router.delete("/api/users/{username}")
async def delete_existing_user(username: str, current_user = Depends(require_admin)):
    """حذف کاربر"""
    if username == "sina":
        raise HTTPException(status_code=403, detail="Cannot delete super admin")
    if username == current_user["username"]:
        raise HTTPException(status_code=403, detail="Cannot delete yourself")
    
    target_user = get_user_by_username(username)
    if target_user and target_user["is_admin"] and current_user["username"] != "sina":
        raise HTTPException(status_code=403, detail="Only sina can delete admins")
    
    delete_user(username)
    return JSONResponse({"status": "success", "message": "User deleted"})
