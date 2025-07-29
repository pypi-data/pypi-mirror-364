# dashboard/logger_service.py
from sqlmodel import Session
from fastapi import BackgroundTasks
import html # <-- 导入 html 模块用于转义

from . import models
from .notifications import send_notification

# 定义哪些级别的日志需要触发通知
NOTIFICATION_LEVELS = {"WARNING", "CRITICAL"}

def add_log(
    db_session: Session, 
    level: str, 
    source: str, 
    message: str,
    background_tasks: BackgroundTasks
):
    """
    Adds a new message to the system log and triggers a notification if the level is high enough.
    """
    # 1. 创建并保存日志条目
    log_entry = models.MessageLog(
        level=level.upper(),
        source=source,
        message=message
    )
    db_session.add(log_entry)
    db_session.commit()

    # 2. 检查是否需要发送通知
    if log_entry.level in NOTIFICATION_LEVELS:
        # --- 修正: 将消息格式从 Markdown 改为 HTML ---
        # 使用 <b> 标签表示粗体, <code> 标签表示等宽字体
        # 使用 html.escape() 来安全地处理用户输入或包含特殊字符的消息内容
        escaped_message = html.escape(log_entry.message)
        
        notification_message = (
            f"<b>🚨 Eops Panel Alert 🚨</b>\n\n"
            f"<b>Level:</b> <code>{log_entry.level}</code>\n"
            f"<b>Source:</b> <code>{log_entry.source}</code>\n"
            f"<b>Time:</b> <code>{log_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</code>\n\n"
            f"<b>Message:</b>\n<pre>{escaped_message}</pre>"
        )
        
        # 使用后台任务发送通知,避免阻塞当前请求
        background_tasks.add_task(send_notification, notification_message, db_session)