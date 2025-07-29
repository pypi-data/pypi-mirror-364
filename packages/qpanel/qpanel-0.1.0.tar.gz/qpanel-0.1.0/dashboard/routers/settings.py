# dashboard/routers/settings.py
import json # <-- 修正: 添加导入
from typing import Optional, Dict, List
from pydantic import BaseModel

from fastapi import APIRouter, Request, Depends, Form, HTTPException, Cookie, status, BackgroundTasks
from fastapi.responses import HTMLResponse, Response, JSONResponse, RedirectResponse
from sqlmodel import Session, select

from .. import models, security
from ..database import get_session
from ..shared import templates, SAFE_BASE_DIR
from ..security import pwd_context
from ..logger_service import add_log

# --- Pydantic Models ---
class PanelSettingsUpdate(BaseModel):
    panel_name: str
    safe_directory: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

# 路由器保持不变
router = APIRouter(tags=["settings"])

# --- Helper Function for settings ---
def get_all_settings(session: Session) -> Dict[str, str]:
    settings_list = session.exec(select(models.PanelSetting)).all()
    settings_dict = {setting.key: setting.value for setting in settings_list}
    settings_dict.setdefault("panel_name", "Eops Panel")
    settings_dict.setdefault("safe_directory", str(SAFE_BASE_DIR))
    return settings_dict

# --- Web Page Routes ---

@router.get("/login", response_class=HTMLResponse)
async def page_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/setup", response_class=HTMLResponse)
async def page_setup(request: Request, session: Session = Depends(get_session)):
    master_pwd_hash = session.get(models.PanelSetting, "master_password_hash")
    if master_pwd_hash:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("setup.html", {"request": request})

@router.get("/trading-settings", response_class=HTMLResponse)
async def page_trading_settings(request: Request):
    return templates.TemplateResponse("trading_settings.html", {"request": request})

@router.get("/panel-settings", response_class=HTMLResponse)
async def page_panel_settings(request: Request, session: Session = Depends(get_session)):
    settings = get_all_settings(session)
    context = {"request": request, "settings": settings}
    return templates.TemplateResponse("panel_settings.html", context)

# --- API Routes for Security & Auth ---

@router.post("/api/setup", response_class=JSONResponse)
async def api_do_setup(
    background_tasks: BackgroundTasks,
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    master_pwd_hash = session.get(models.PanelSetting, "master_password_hash")
    if master_pwd_hash:
        raise HTTPException(status_code=400, detail="Panel is already configured.")
    
    hashed_password = security.get_password_hash(password)
    setting = models.PanelSetting(key="master_password_hash", value=hashed_password)
    session.add(setting)
    session.commit()
    security.initialize_fernet(password)

    add_log(session, "CRITICAL", "Security", "Panel master password has been set up.", background_tasks)
    
    response = JSONResponse(content={"status": "success", "message": "Setup complete. Redirecting to login..."})
    return response

@router.post("/api/login")
async def api_do_login(
    response: Response,
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    pwd_setting = session.get(models.PanelSetting, "master_password_hash")
    if not pwd_setting or not security.verify_password(password, pwd_setting.value):
        raise HTTPException(status_code=401, detail="Invalid password.")
        
    security.initialize_fernet(password)
    response.set_cookie(key="eops_session", value=password, httponly=True, samesite="lax")
    return {"status": "success"}

@router.post("/api/logout")
async def api_do_logout(response: Response):
    response.delete_cookie("eops_session")
    return {"status": "success"}

@router.post("/api/panel/password", response_class=JSONResponse)
def update_password(
    update: PasswordUpdate, 
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    pwd_setting = session.get(models.PanelSetting, "master_password_hash")
    if not pwd_setting or not security.verify_password(update.current_password, pwd_setting.value):
        raise HTTPException(status_code=403, detail="Incorrect current password.")
    
    new_hashed_password = security.get_password_hash(update.new_password)
    pwd_setting.value = new_hashed_password
    session.add(pwd_setting)
    
    api_keys = session.exec(select(models.ApiKey)).all()
    key_count = len(api_keys)
    for key in api_keys:
        session.delete(key)
        
    session.commit()
    security.initialize_fernet(update.new_password)
    
    add_log(session, "CRITICAL", "Security", f"Master password has been changed. {key_count} API key(s) were cleared.", background_tasks)
    
    return JSONResponse(content={"status": "success", "message": f"Password updated. All {key_count} API keys have been cleared."})

# --- API Routes for Panel Settings ---
@router.get("/api/panel/settings", response_class=JSONResponse)
def api_get_panel_settings(session: Session = Depends(get_session)):
    return JSONResponse(content=get_all_settings(session))

@router.post("/api/panel/settings", response_class=JSONResponse)
def api_update_panel_settings(
    settings_update: PanelSettingsUpdate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    update_data = settings_update.dict()
    
    for key, value in update_data.items():
        setting = models.PanelSetting(key=key, value=str(value))
        session.merge(setting)

    session.commit()
    add_log(session, "INFO", "Settings", f"Panel settings updated: {json.dumps(update_data)}", background_tasks)
    return JSONResponse(content={"status": "success", "message": "Settings updated successfully."})

# --- API Routes for API Keys ---
@router.get("/api/keys/list", response_class=HTMLResponse)
def api_get_keys_list(request: Request, session: Session = Depends(get_session)):
    keys = session.exec(select(models.ApiKey).order_by(models.ApiKey.name)).all()
    return templates.TemplateResponse("_api_keys_table.html", {"request": request, "keys": keys})

@router.post("/api/keys", response_class=Response)
def api_create_key(
    background_tasks: BackgroundTasks, # <-- 修正: 调整参数顺序
    name: str = Form(...), 
    exchange: str = Form(...),
    api_key: str = Form(...), 
    secret_key: Optional[str] = Form(None), 
    passphrase: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    if session.exec(select(models.ApiKey).where(models.ApiKey.name == name)).first():
        raise HTTPException(status_code=400, detail=f"API Key with name '{name}' already exists.")
    
    new_key = models.ApiKey(
        name=name, exchange=exchange, api_key=security.encrypt_data(api_key),
        secret_key=security.encrypt_data(secret_key) if secret_key else None,
        passphrase=security.encrypt_data(passphrase) if passphrase else None)
    session.add(new_key)
    session.commit()

    add_log(session, "INFO", "Security", f"API Key '{name}' for exchange '{exchange}' was created.", background_tasks)
    return Response(status_code=200, headers={"HX-Trigger": "apiKeyUpdated"})

@router.delete("/api/keys/{key_id}", response_class=Response)
def api_delete_key(
    key_id: int, 
    background_tasks: BackgroundTasks, # <-- 修正: 调整参数顺序
    session: Session = Depends(get_session)
):
    key = session.get(models.ApiKey, key_id)
    if not key: raise HTTPException(404)
    
    key_name = key.name
    session.delete(key)
    session.commit()

    add_log(session, "WARNING", "Security", f"API Key '{key_name}' was deleted.", background_tasks)
    return Response(status_code=200, headers={"HX-Trigger": "apiKeyUpdated"})

# --- API for Message Logs ---
@router.get("/api/panel/message-logs", response_class=HTMLResponse)
def api_get_message_logs(request: Request, session: Session = Depends(get_session)):
    logs = session.exec(
        select(models.MessageLog).order_by(models.MessageLog.timestamp.desc()).limit(100)
    ).all()
    return templates.TemplateResponse("_message_logs_table.html", {"request": request, "logs": logs})