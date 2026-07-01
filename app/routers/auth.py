from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import JSONResponse, RedirectResponse
from app.models.models import LoginData
from app.services.auth_service import authenticate_user, create_user_session, get_user_from_session, remove_session

router = APIRouter()

@router.post("/api/login")
async def login(data: LoginData, response: Response):
    """ورود کاربر"""
    user = authenticate_user(data.username, data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_id = create_user_session(data.username)
    
    resp = JSONResponse({
        "status": "success",
        "username": user["username"],
        "is_admin": user["is_admin"]
    })
    
    resp.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=86400,
        path="/"
    )
    
    return resp

@router.post("/api/logout")
async def logout(request: Request):
    """خروج کاربر"""
    session_id = request.cookies.get("session_id")
    if session_id:
        remove_session(session_id)
    
    response = RedirectResponse(url="/")
    response.delete_cookie("session_id", path="/")
    return response

@router.get("/api/me")
async def get_me(request: Request):
    """دریافت اطلاعات کاربر فعلی"""
    session_id = request.cookies.get("session_id")
    user = get_user_from_session(session_id)
    
    if not user:
        return JSONResponse({"authenticated": False})
    
    return JSONResponse({
        "authenticated": True,
        "username": user["username"],
        "is_admin": user["is_admin"]
    })