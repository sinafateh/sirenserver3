from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.routers import auth, users, data, dashboard, notifications
from app.database.database import init_db

# ==================== Middleware برای اصلاح CSP ====================
class FixCSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # تنظیم CSP با اجازه اجرای 'unsafe-eval' و 'unsafe-inline'
        csp_header = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-src 'self'; "
            "object-src 'none'"
        )
        
        # جایگزینی یا اضافه کردن هدر CSP
        response.headers["Content-Security-Policy"] = csp_header
        
        return response

# راه‌اندازی دیتابیس
init_db()

# ایجاد اپلیکیشن
app = FastAPI(
    title="Siren Tester API",
    description="سیستم تست کنترل سایرن",
    version="2.0"
)

# ==================== اضافه کردن Middlewareها ====================
app.add_middleware(FixCSPMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ثبت روت‌ها ====================
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
