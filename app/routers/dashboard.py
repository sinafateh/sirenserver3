from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from app.services.auth_service import get_user_from_session
import os

router = APIRouter()

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")

def read_html_file(filename: str, **kwargs):
    """خواندن فایل HTML و جایگزینی متغیرها"""
    file_path = os.path.join(TEMPLATE_DIR, filename)
    
    if not os.path.exists(file_path):
        return HTMLResponse(content=f"<h1>File {filename} not found!</h1>", status_code=404)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # جایگزینی متغیرها
    content = content.replace('USERNAME_PLACEHOLDER', kwargs.get('username', 'کاربر'))
    content = content.replace('SESSION_IS_ADMIN = true', f'SESSION_IS_ADMIN = {str(kwargs.get("is_admin", False)).lower()}')
    content = content.replace('SESSION_IS_SINA = false', f'SESSION_IS_SINA = {str(kwargs.get("is_sina", False)).lower()}')
    
    return HTMLResponse(content=content)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """صفحه اصلی"""
    session_id = request.cookies.get("session_id")
    user = get_user_from_session(session_id)
    
    if not user:
        return read_html_file("login.html")
    
    return read_html_file("dashboard.html",
        username=user["username"],
        is_admin=user["is_admin"],
        is_sina=user["username"] == "sina"
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """صفحه داشبورد"""
    session_id = request.cookies.get("session_id")
    user = get_user_from_session(session_id)
    
    if not user:
        return RedirectResponse(url="/", status_code=302)
    
    return read_html_file("dashboard.html",
        username=user["username"],
        is_admin=user["is_admin"],
        is_sina=user["username"] == "sina"
    )

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """صفحه لاگین"""
    return read_html_file("login.html")