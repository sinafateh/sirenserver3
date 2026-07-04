from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.routers import auth, users, data, dashboard, notifications
from app.database.database import init_db

# ==================== قوی‌ترین Middleware برای حذف کامل CSP ====================
class RemoveAllSecurityHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # لیست همه هدرهای امنیتی که باید حذف بشن
        headers_to_remove = [
            "content-security-policy",
            "content-security-policy-report-only",
            "x-content-security-policy",
            "x-webkit-csp",
            "x-frame-options",
            "x-xss-protection",
            "referrer-policy"
        ]
        
        for header in headers_to_remove:
            if header in response.headers:
                del response.headers[header]
        
        # هیچ هدر CSP اضافه نمیکنیم - کاملاً حذفش میکنیم
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
# اولویت: این middleware باید اولین باشه
app.add_middleware(RemoveAllSecurityHeaders)

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
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        # مهم: این پارامتر رو اضافه کن تا CSP غیرفعال بشه
        headers=[("Content-Security-Policy", "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:;")]
    )
