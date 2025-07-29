# dashboard/notifications.py
import httpx
import json
import html # 导入 html 模块
from sqlmodel import Session, select

from . import models
from .database import engine # 使用 engine 来创建新会话

# --- Private Sender Functions ---

async def _send_telegram(config: dict, message: str):
    """Sends a message via Telegram Bot."""
    token = config.get("bot_token")
    chat_id = config.get("chat_id")
    if not token or not chat_id:
        raise ValueError("Telegram config requires 'bot_token' and 'chat_id'.")
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=10.0)
        if response.status_code != 200:
            error_details = response.json()
            raise httpx.HTTPStatusError(
                f"Error from Telegram API: {error_details.get('description', 'Unknown error')}",
                request=response.request,
                response=response
            )

async def _send_webhook(config: dict, message: str):
    """Sends a message via a generic webhook."""
    url = config.get("webhook_url")
    if not url:
        raise ValueError("Webhook config requires 'webhook_url'.")
        
    payload = {"content": message}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=10.0)
        response.raise_for_status()

# --- Public Notification Dispatcher ---

async def send_notification(message: str, db_session: Session):
    """
    Dispatches a notification to all enabled channels and logs the result.
    This function is intended to be called as a background task.
    """
    # 在后台任务中, 我们应该从 engine 创建一个新的会话来保证线程安全
    with Session(engine) as session:
        statement = select(models.NotificationChannel).where(models.NotificationChannel.is_enabled == True)
        channels = session.exec(statement).all()
        
        for channel in channels:
            status = "failed"
            details = ""
            try:
                config = json.loads(channel.config_json)
                
                if channel.channel_type == 'telegram':
                    await _send_telegram(config, message)
                elif channel.channel_type == 'webhook':
                    webhook_message = message.replace('<b>', '**').replace('</b>', '**').replace('<code>', '`').replace('</code>', '`').replace('<pre>', '```\n').replace('</pre>', '\n```').replace('🚨', '')
                    await _send_webhook(config, webhook_message)
                
                status = "success"

            except Exception as e:
                details = f"Error Type: {type(e).__name__}\nDetails: {str(e)}"
                print(f"Failed to send notification to '{channel.name}': {details}")

            log_entry = models.NotificationLog(
                channel_id=channel.id,
                channel_name=channel.name,
                message=message,
                status=status,
                details=details
            )
            session.add(log_entry)
        
        session.commit()

# --- Test Function (Corrected Logic) ---

async def send_test_notification(channel: models.NotificationChannel, db_session: Session):
    """
    Sends a test message to a *specific* channel and logs the attempt directly.
    This avoids circular dependencies with the logger_service.
    """
    message_html = f"<b>✅ Eops Panel Test</b>\n\nThis is a test notification for the channel '<b>{html.escape(channel.name)}</b>'. If you receive this, the configuration is correct."
    
    status = "failed"
    details = ""
    try:
        config = json.loads(channel.config_json)
        if channel.channel_type == 'telegram':
            await _send_telegram(config, message_html)
        elif channel.channel_type == 'webhook':
            webhook_message = f"✅ Eops Panel Test\n\nThis is a test notification for the channel '**{channel.name}**'. If you receive this, the configuration is correct."
            await _send_webhook(config, webhook_message)
        status = "success"

    except Exception as e:
        details = f"Error Type: {type(e).__name__}\nDetails: {str(e)}"
        print(f"Failed to send test notification to '{channel.name}': {details}")

    # Log the test attempt directly to the NotificationLog table
    with Session(engine) as session:
        log_entry = models.NotificationLog(
            channel_id=channel.id,
            channel_name=channel.name,
            message="[TEST MESSAGE]", # Keep the message in the log concise
            status=status,
            details=details
        )
        session.add(log_entry)
        session.commit()