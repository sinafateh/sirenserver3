import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "siren_data.db")

def get_db_connection():
    """ایجاد اتصال به دیتابیس"""
    return sqlite3.connect(DB_PATH)

def init_db():
    """راه‌اندازی اولیه دیتابیس"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # جدول کاربران
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # جدول رکوردهای تست
    c.execute('''CREATE TABLE IF NOT EXISTS test_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT NOT NULL,
        operator TEXT NOT NULL,
        flasher_type BOOLEAN DEFAULT 0,
        max_mode2 REAL DEFAULT 0,
        max_mode3 REAL DEFAULT 0,
        fault_mode2 BOOLEAN DEFAULT 0,
        fault_mode3 BOOLEAN DEFAULT 0,
        passed BOOLEAN DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # جدول سشن‌ها
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP DEFAULT (datetime('now', '+1 day'))
    )''')
    
    # جدول اعلان‌ها
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        receiver TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read BOOLEAN DEFAULT 0,
        is_broadcast BOOLEAN DEFAULT 0,
        notification_type TEXT DEFAULT 'admin_message',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # کاربر پیش‌فرض
    password_hash = hashlib.sha256("sina".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)", 
              ("sina", password_hash))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# ============ توابع کاربران ============
def get_all_users():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT username, is_admin FROM users")
    rows = c.fetchall()
    conn.close()
    return [{"username": row[0], "is_admin": bool(row[1])} for row in rows]

def get_user_by_username(username: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT username, is_admin FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"username": row[0], "is_admin": bool(row[1])}
    return None

def get_user_with_password(username: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT username, password_hash, is_admin FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"username": row[0], "password_hash": row[1], "is_admin": bool(row[2])}
    return None

def add_user(username: str, password_hash: str, is_admin: bool = False):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                  (username, password_hash, is_admin))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def delete_user(username: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    return True

# ============ توابع سشن ============
def create_session(session_id: str, username: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO sessions (session_id, username, expires_at) VALUES (?, ?, datetime('now', '+1 day'))",
              (session_id, username))
    conn.commit()
    conn.close()

def get_session_user(session_id: str):
    if not session_id:
        return None
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT s.username, u.is_admin 
                 FROM sessions s 
                 JOIN users u ON s.username = u.username 
                 WHERE s.session_id = ? AND s.expires_at > datetime('now')''', 
              (session_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"username": row[0], "is_admin": bool(row[1])}
    return None

def delete_session(session_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

# ============ توابع رکوردها ============
def get_test_records(limit: int = 30):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT barcode, operator, flasher_type, max_mode2, max_mode3,
                        fault_mode2, fault_mode3, passed, timestamp
                 FROM test_records 
                 ORDER BY timestamp DESC 
                 LIMIT ?''', (limit,))
    rows = c.fetchall()
    conn.close()
    
    return [{
        "barcode": row[0],
        "operator": row[1],
        "flasher_type": bool(row[2]),
        "max_mode2": row[3],
        "max_mode3": row[4],
        "fault_mode2": bool(row[5]),
        "fault_mode3": bool(row[6]),
        "passed": bool(row[7]),
        "timestamp": row[8]
    } for row in rows]

# ==================== توابع اعلان‌ها ====================

def create_notification(sender: str, receiver: str, title: str, message: str, is_broadcast: bool = False):
    """ایجاد اعلان جدید"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO notifications 
                 (sender, receiver, title, message, is_broadcast) 
                 VALUES (?, ?, ?, ?, ?)''',
              (sender, receiver, title, message, is_broadcast))
    conn.commit()
    conn.close()
    return True

def get_notifications_for_user(username: str, limit: int = 50):
    """دریافت اعلان‌های یک کاربر (خودی + broadcast + پیام‌های ارسالی خودش)"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT id, sender, receiver, title, message, is_read, is_broadcast, notification_type, created_at
                 FROM notifications 
                 WHERE receiver = ? OR is_broadcast = 1 OR sender = ?
                 ORDER BY created_at DESC 
                 LIMIT ?''', (username, username, limit))
    rows = c.fetchall()
    conn.close()
    
    notifications = []
    for row in rows:
        notifications.append({
            "id": row[0],
            "sender": row[1],
            "receiver": row[2],
            "title": row[3],
            "message": row[4],
            "is_read": bool(row[5]),
            "is_broadcast": bool(row[6]),
            "notification_type": row[7],
            "created_at": row[8],
            "is_own": row[1] == username  # مشخص می‌کند که آیا کاربر خودش ارسال کرده
        })
    return notifications

def get_unread_count(username: str):
    """تعداد اعلان‌های خوانده نشده (فقط پیام‌های دریافتی، نه ارسالی)"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) 
                 FROM notifications 
                 WHERE (receiver = ? OR is_broadcast = 1) AND is_read = 0''', 
              (username,))
    count = c.fetchone()[0]
    conn.close()
    return count

def mark_notification_as_read(notification_id: int, username: str):
    """علامت‌گذاری اعلان به عنوان خوانده شده (فقط برای پیام‌های دریافتی)"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''UPDATE notifications 
                 SET is_read = 1 
                 WHERE id = ? AND (receiver = ? OR is_broadcast = 1)''', 
              (notification_id, username))
    conn.commit()
    conn.close()
    return True

def delete_notification(notification_id: int):
    """حذف اعلان (فقط ادمین)"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
    conn.commit()
    conn.close()
    return True

def get_all_notifications(limit: int = 100):
    """دریافت همه اعلان‌ها (برای ادمین)"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT id, sender, receiver, title, message, is_read, is_broadcast, notification_type, created_at
                 FROM notifications 
                 ORDER BY created_at DESC 
                 LIMIT ?''', (limit,))
    rows = c.fetchall()
    conn.close()
    
    notifications = []
    for row in rows:
        notifications.append({
            "id": row[0],
            "sender": row[1],
            "receiver": row[2],
            "title": row[3],
            "message": row[4],
            "is_read": bool(row[5]),
            "is_broadcast": bool(row[6]),
            "notification_type": row[7],
            "created_at": row[8]
        })
    return notifications

# ==================== توابع مدیریت پیام‌ها (جدید) ====================

def delete_user_notification(notification_id: int, username: str):
    """حذف اعلان توسط کاربر (فقط پیام‌های خودش یا broadcast یا پیام‌های ارسالی خودش)"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''DELETE FROM notifications 
                 WHERE id = ? AND (receiver = ? OR is_broadcast = 1 OR sender = ?)''', 
              (notification_id, username, username))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def delete_notification_by_admin(notification_id: int):
    """حذف اعلان توسط ادمین (هر پیامی)"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def delete_all_user_notifications(username: str):
    """حذف همه پیام‌های یک کاربر (پیام‌های خودش + broadcast + پیام‌های ارسالی خودش)"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''DELETE FROM notifications 
                 WHERE receiver = ? OR is_broadcast = 1 OR sender = ?''', (username, username))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected

def delete_all_notifications():
    """حذف همه پیام‌ها (فقط ادمین)"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM notifications")
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected