from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.models.models import NotificationCreate
from app.services.auth_service import get_user_from_session
from app.services.notification_service import NotificationService
from app.database.database import get_all_users

router = APIRouter()

@router.post("/api/notifications")
async def send_notification(request: Request, data: NotificationCreate):
    """ارسال اعلان جدید (فقط ادمین)"""
    session_id = request.cookies.get("session_id")
    current_user = get_user_from_session(session_id)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can send notifications")
    
    result = NotificationService.send_notification(
        sender=current_user["username"],
        receiver=data.receiver,
        title=data.title,
        message=data.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return JSONResponse(result)

@router.get("/api/notifications")
async def get_notifications(request: Request, limit: int = 50):
    """دریافت اعلان‌های کاربر فعلی (شامل پیام‌های ارسالی خودش)"""
    session_id = request.cookies.get("session_id")
    current_user = get_user_from_session(session_id)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    notifications = NotificationService.get_user_notifications(
        current_user["username"], 
        limit
    )
    
    return JSONResponse(notifications)

@router.get("/api/notifications/unread")
async def get_unread_count(request: Request):
    """تعداد اعلان‌های خوانده نشده (فقط دریافتی)"""
    session_id = request.cookies.get("session_id")
    current_user = get_user_from_session(session_id)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    count = NotificationService.get_unread_count(current_user["username"])
    return JSONResponse({"unread_count": count})

@router.post("/api/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int, request: Request):
    """علامت‌گذاری اعلان به عنوان خوانده شده"""
    session_id = request.cookies.get("session_id")
    current_user = get_user_from_session(session_id)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = NotificationService.mark_as_read(notification_id, current_user["username"])
    return JSONResponse({"status": "success"})

@router.delete("/api/notifications/{notification_id}")
async def delete_notification_route(notification_id: int, request: Request):
    """حذف پیام (کاربر عادی: فقط پیام‌های خودش/ارسالی خودش، ادمین: هر پیامی)"""
    session_id = request.cookies.get("session_id")
    current_user = get_user_from_session(session_id)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # اگه ادمین باشه، می‌تونه هر پیامی رو حذف کنه
    if current_user.get("is_admin"):
        result = NotificationService.delete_notification_by_admin(notification_id)
        if not result:
            raise HTTPException(status_code=404, detail="Notification not found")
        return JSONResponse({"status": "success", "message": "Notification deleted by admin"})
    
    # کاربر عادی فقط پیام‌های خودش رو می‌تونه حذف کنه (شامل ارسالی‌های خودش)
    result = NotificationService.delete_notification_for_user(
        notification_id, 
        current_user["username"]
    )
    
    if not result:
        raise HTTPException(
            status_code=403, 
            detail="You can only delete your own notifications"
        )
    
    return JSONResponse({"status": "success", "message": "Notification deleted"})

@router.delete("/api/notifications/clear/all")
async def clear_all_notifications_route(request: Request):
    """پاک کردن همه پیام‌ها (فقط ادمین)"""
    session_id = request.cookies.get("session_id")
    current_user = get_user_from_session(session_id)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can clear all notifications")
    
    count = NotificationService.clear_all_notifications()
    return JSONResponse({
        "status": "success", 
        "message": f"All {count} notifications cleared"
    })

@router.delete("/api/notifications/clear/my")
async def clear_my_notifications_route(request: Request):
    """پاک کردن همه پیام‌های خودم (شامل ارسالی‌های خودم)"""
    session_id = request.cookies.get("session_id")
    current_user = get_user_from_session(session_id)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    count = NotificationService.clear_all_user_notifications(current_user["username"])
    return JSONResponse({
        "status": "success", 
        "message": f"{count} notifications cleared"
    })

@router.get("/api/notifications/users")
async def get_users_list(request: Request):
    """دریافت لیست کاربران برای انتخاب گیرنده (فقط ادمین)"""
    session_id = request.cookies.get("session_id")
    current_user = get_user_from_session(session_id)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = get_all_users()
    users = [u for u in users if u["username"] != current_user["username"]]
    return JSONResponse(users)