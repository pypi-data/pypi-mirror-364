# dashboard/routers/notifications.py
import json
from typing import Optional

from fastapi import APIRouter, Request, Depends, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, Response
from sqlmodel import Session, select

from .. import models
from ..database import get_session
from ..shared import templates
from ..notifications import send_test_notification

router = APIRouter(tags=["notifications"])

# --- Page Rendering ---
@router.get("/notification-center", response_class=HTMLResponse)
async def page_notification_center(request: Request):
    # This route is now a sub-component, so it doesn't extend base.html
    return templates.TemplateResponse("notification_center.html", {"request": request})

# --- 新增: 统一页面的渲染路由 ---
@router.get("/logging-and-notifications", response_class=HTMLResponse)
async def page_logging_and_notifications(request: Request):
    """Renders the combined logging and notifications view for the settings tab."""
    return templates.TemplateResponse("_logging_and_notifications.html", {"request": request})

# --- API for Notification Channels ---
@router.get("/api/notifications/channels", response_class=HTMLResponse)
def api_get_channels_list(request: Request, session: Session = Depends(get_session)):
    # ... (code remains the same)
    channels = session.exec(select(models.NotificationChannel).order_by(models.NotificationChannel.name)).all()
    return templates.TemplateResponse("_notification_channels_table.html", {"request": request, "channels": channels})

@router.post("/api/notifications/channels", response_class=Response)
def api_create_channel(
    session: Session = Depends(get_session),
    name: str = Form(...),
    channel_type: str = Form(...),
    is_enabled: bool = Form(True),
    bot_token: Optional[str] = Form(None),
    chat_id: Optional[str] = Form(None),
    webhook_url: Optional[str] = Form(None),
):
    # ... (code remains the same)
    if session.exec(select(models.NotificationChannel).where(models.NotificationChannel.name == name)).first():
        raise HTTPException(status_code=400, detail=f"A channel with the name '{name}' already exists.")
    config = {}
    if channel_type == "telegram":
        if not bot_token or not chat_id: raise HTTPException(status_code=400, detail="Bot Token and Chat ID are required for Telegram.")
        config = {"bot_token": bot_token, "chat_id": chat_id}
    elif channel_type == "webhook":
        if not webhook_url: raise HTTPException(status_code=400, detail="Webhook URL is required.")
        config = {"webhook_url": webhook_url}
    else:
        raise HTTPException(status_code=400, detail="Invalid channel type.")
    new_channel = models.NotificationChannel(name=name, channel_type=channel_type, is_enabled=is_enabled, config_json=json.dumps(config))
    session.add(new_channel)
    session.commit()
    return Response(status_code=200, headers={"HX-Trigger": "channelsChanged"})

@router.delete("/api/notifications/channels/{channel_id}", response_class=Response)
def api_delete_channel(channel_id: int, session: Session = Depends(get_session)):
    # ... (code remains the same)
    channel = session.get(models.NotificationChannel, channel_id)
    if not channel: raise HTTPException(status_code=404, detail="Channel not found.")
    logs_to_delete = session.exec(select(models.NotificationLog).where(models.NotificationLog.channel_id == channel_id)).all()
    for log in logs_to_delete:
        session.delete(log)
    session.delete(channel)
    session.commit()
    return Response(status_code=200)

@router.post("/api/notifications/channels/{channel_id}/test", response_class=Response)
async def api_test_channel(
    channel_id: int, 
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    # ... (code remains the same)
    channel = session.get(models.NotificationChannel, channel_id)
    if not channel: raise HTTPException(status_code=404, detail="Channel not found.")
    background_tasks.add_task(send_test_notification, channel, session)
    return Response(content="Test notification sent. Check history for status.", headers={"HX-Trigger": "logsChanged"})

# --- API for Notification Logs ---
@router.get("/api/notifications/logs", response_class=HTMLResponse)
async def api_get_logs_list(request: Request, session: Session = Depends(get_session)):
    """Fetches and renders the table of recent notification logs."""
    logs = session.exec(
        select(models.NotificationLog).order_by(models.NotificationLog.timestamp.desc()).limit(20)
    ).all()
    # Note: I renamed the template to be more specific
    return templates.TemplateResponse("_notification_history_table.html", {"request": request, "logs": logs})