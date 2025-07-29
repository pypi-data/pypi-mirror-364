# dashboard/auth_middleware.py
from fastapi import Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlmodel import Session, select
from datetime import datetime

from .database import engine
from . import models
from . import security

class AuthMiddleware(BaseHTTPMiddleware):
    async def verify_api_key(self, token: str) -> bool:
        """
        Verifies a bearer token against the PanelApiKey database.
        This runs in its own session to be independent.
        """
        with Session(engine) as session:
            api_enabled_setting = session.get(models.PanelSetting, "panel_api_enabled")
            if not api_enabled_setting or api_enabled_setting.value != 'true':
                return False

            try:
                prefix, _, secret = token.partition('_')
                if not prefix or not secret: return False
                prefix_with_underscore = f"{prefix}_"
            except Exception:
                return False

            key_record = session.exec(
                select(models.PanelApiKey).where(models.PanelApiKey.key_prefix == prefix_with_underscore)
            ).first()

            if not key_record or not key_record.is_active:
                return False

            if not security.pwd_context.verify(token, key_record.hashed_key):
                return False
            
            key_record.last_used = datetime.utcnow()
            session.add(key_record)
            session.commit()
            return True

    async def dispatch(self, request: Request, call_next):
        # 路径白名单 (对所有认证方式都豁免)
        allowed_paths = ["/login", "/setup", "/static", "/docs", "/openapi.json"]
        api_allowed_paths = ["/api/setup", "/api/login"]

        is_allowed = any(request.url.path.startswith(p) for p in allowed_paths)
        is_api_allowed = any(request.url.path.startswith(p) for p in api_allowed_paths)
        if is_allowed or is_api_allowed:
            return await call_next(request)

        # 检查数据库是否已设置密码
        with Session(engine) as session:
            master_pwd_hash = session.get(models.PanelSetting, "master_password_hash")
            if not master_pwd_hash:
                return RedirectResponse(url="/setup", status_code=status.HTTP_303_SEE_OTHER)

        # --- 新增: API Key 认证逻辑 ---
        if request.url.path.startswith('/api/'):
            auth_header = request.headers.get("Authorization")
            if auth_header:
                scheme, _, token = auth_header.partition(' ')
                if scheme.lower() == 'bearer' and token:
                    is_valid = await self.verify_api_key(token)
                    if is_valid:
                        # API Key 验证通过, 直接处理请求
                        return await call_next(request)
                    else:
                        # 提供了无效的 Token, 直接拒绝
                        return JSONResponse(status_code=401, content={"detail": "Invalid or disabled API Key"})

        # --- 原有的 Cookie 会话认证逻辑 (作为 API Key 认证失败后的回退) ---
        session_cookie = request.cookies.get("eops_session")
        if not session_cookie:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        with Session(engine) as session:
            master_pwd_hash = session.get(models.PanelSetting, "master_password_hash")
            if security.verify_password(session_cookie, master_pwd_hash.value):
                if not security.fernet:
                    security.initialize_fernet(session_cookie)
            else:
                return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

        # 所有检查通过, 继续处理请求
        response = await call_next(request)
        return response