from fastapi import APIRouter, Header, Depends
from fastapi.responses import JSONResponse
from app.models.models import SirenData
from app.services.auth_service import get_user_from_session
from app.database.database import get_test_records

router = APIRouter()

# داده موقت
last_data = {
    "current": 0,
    "mode": 1,
    "over": False,
    "testing": False,
    "barcode": None,
    "operator": None,
    "limit": 50.5,
    "elapsed": 0
}

def get_current_user_optional(session_id: str = Header(None)):
    """دریافت کاربر (اختیاری) از Header"""
    if not session_id:
        return None
    return get_user_from_session(session_id)

@router.post("/api/data")
async def receive_data(data: SirenData, current_user = Depends(get_current_user_optional)):
    """دریافت داده از ESP32 (نیاز به لاگین ندارد)"""
    global last_data
    last_data = {
        "current": data.current,
        "mode": data.mode,
        "over": data.over,
        "testing": data.testing,
        "barcode": data.barcode,
        "operator": data.operator or (current_user["username"] if current_user else None),
        "limit": data.limit or 50.5,
        "elapsed": data.elapsed or 0
    }
    return JSONResponse({"status": "ok"})

@router.get("/api/last")
async def get_last_data():
    """دریافت آخرین داده"""
    return JSONResponse(last_data)

@router.get("/api/records")
async def get_records():
    """دریافت تاریخچه تست‌ها"""
    return JSONResponse(get_test_records())
