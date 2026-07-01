from app.database.database import (
    create_notification, 
    get_notifications_for_user, 
    get_unread_count,
    mark_notification_as_read,
    delete_notification,
    get_all_notifications,
    get_user_by_username,
    delete_user_notification,
    delete_notification_by_admin,
    delete_all_user_notifications,
    delete_all_notifications
)

class NotificationService:
    
    @staticmethod
    def send_notification(sender: str, receiver: str, title: str, message: str, is_broadcast: bool = False):
        """ارسال اعلان جدید"""
        if receiver.upper() == "ALL":
            is_broadcast = True
            receiver = "ALL"
        
        if not is_broadcast:
            user = get_user_by_username(receiver)
            if not user:
                return {"error": f"User '{receiver}' not found"}
        
        create_notification(sender, receiver, title, message, is_broadcast)
        
        # پیام برای خود فرستنده هم نمایش داده میشه (با is_own=true)
        return {"status": "success", "message": "Notification sent"}
    
    @staticmethod
    def get_user_notifications(username: str, limit: int = 50):
        """دریافت اعلان‌های کاربر (شامل پیام‌های ارسالی خودش)"""
        return get_notifications_for_user(username, limit)
    
    @staticmethod
    def get_unread_count(username: str):
        """تعداد اعلان‌های خوانده نشده (فقط پیام‌های دریافتی، نه ارسالی)"""
        return get_unread_count(username)
    
    @staticmethod
    def mark_as_read(notification_id: int, username: str):
        """علامت‌گذاری به عنوان خوانده شده (فقط برای پیام‌های دریافتی)"""
        return mark_notification_as_read(notification_id, username)
    
    @staticmethod
    def delete_notification_for_user(notification_id: int, username: str):
        """حذف پیام توسط کاربر (فقط پیام‌های خودش یا ارسالی خودش)"""
        return delete_user_notification(notification_id, username)
    
    @staticmethod
    def delete_notification_by_admin(notification_id: int):
        """حذف پیام توسط ادمین (هر پیامی)"""
        return delete_notification_by_admin(notification_id)
    
    @staticmethod
    def clear_all_user_notifications(username: str):
        """پاک کردن همه پیام‌های یک کاربر (شامل ارسالی‌های خودش)"""
        return delete_all_user_notifications(username)
    
    @staticmethod
    def clear_all_notifications():
        """پاک کردن همه پیام‌ها (فقط ادمین)"""
        return delete_all_notifications()