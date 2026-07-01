from fastapi import FastAPI
from app.routers import auth, users, data, dashboard, notifications
from app.database.database import init_db

# راه‌اندازی دیتابیس
init_db()

# ایجاد اپلیکیشن
app = FastAPI(
    title="Siren Tester API",
    description="سیستم تست کنترل سایرن",
    version="2.0"
)

# ثبت روت‌ها
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(data.router)
app.include_router(dashboard.router)
app.include_router(notifications.router)

@app.get("/health")
async def health_check():
    """بررسی سلامت سرور"""
    return {"status": "healthy", "version": "2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)