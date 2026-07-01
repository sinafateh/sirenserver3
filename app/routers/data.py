from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.models.models import SirenData

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

@router.post("/api/data")
async def receive_data(data: SirenData):
    """دریافت داده از ESP32"""
    global last_data
    last_data = {
        "current": data.current,
        "mode": data.mode,
        "over": data.over,
        "testing": data.testing,
        "barcode": data.barcode,
        "operator": data.operator,
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
    from app.database.database import get_test_records
    return JSONResponse(get_test_records())