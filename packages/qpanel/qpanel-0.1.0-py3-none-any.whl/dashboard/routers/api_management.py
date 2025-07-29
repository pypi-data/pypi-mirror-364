# dashboard/routers/api_management.py
import os
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sqlmodel import Session, select

from .. import models, security
from ..database import get_session
from ..shared import templates

router = APIRouter(tags=["api_management"])

@router.get("/api-management", response_class=HTMLResponse)
async def page_api_management(request: Request):
    return templates.TemplateResponse("api_management.html", {"request": request})

@router.get("/api/panel-keys/status", response_class=JSONResponse)
def api_get_panel_api_status(session: Session = Depends(get_session)):
    setting = session.get(models.PanelSetting, "panel_api_enabled")
    is_enabled = setting and setting.value == 'true'
    return {"enabled": is_enabled}

@router.post("/api/panel-keys/toggle", response_class=JSONResponse)
def api_toggle_panel_api(session: Session = Depends(get_session)):
    setting = session.get(models.PanelSetting, "panel_api_enabled")
    if setting:
        is_enabled = setting.value == 'true'
        setting.value = 'false' if is_enabled else 'true'
    else:
        setting = models.PanelSetting(key="panel_api_enabled", value='true')
    
    session.add(setting)
    session.commit()
    return {"enabled": setting.value == 'true'}

@router.get("/api/panel-keys/list", response_class=HTMLResponse)
def api_get_panel_keys_list(request: Request, session: Session = Depends(get_session)):
    keys = session.exec(select(models.PanelApiKey).order_by(models.PanelApiKey.created_at.desc())).all()
    return templates.TemplateResponse("_panel_api_keys_table.html", {"request": request, "keys": keys})

@router.post("/api/panel-keys", response_class=JSONResponse)
def api_create_panel_key(session: Session = Depends(get_session), name: str = Form(...)):
    if session.exec(select(models.PanelApiKey).where(models.PanelApiKey.name == name)).first():
        raise HTTPException(status_code=400, detail=f"Key with name '{name}' already exists.")

    prefix = "qpk"
    secret = os.urandom(24).hex()
    full_key = f"{prefix}_{secret}"
    hashed_key = security.get_password_hash(full_key)

    new_key = models.PanelApiKey(
        name=name,
        key_prefix=f"{prefix}_",
        hashed_key=hashed_key,
    )
    session.add(new_key)
    session.commit()
    return {"status": "success", "key_name": name, "full_key": full_key}

@router.delete("/api/panel-keys/{key_id}", response_class=Response)
def api_delete_panel_key(key_id: int, session: Session = Depends(get_session)):
    key = session.get(models.PanelApiKey, key_id)
    if not key: raise HTTPException(404)
    session.delete(key)
    session.commit()
    return Response(status_code=200, headers={"HX-Trigger": "panelKeyUpdated"})