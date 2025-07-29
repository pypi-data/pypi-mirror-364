# eops_dashboard/models.py
from typing import Optional, List, Any
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from pathlib import Path

# ... (ApiKey, StrategyProject, NotificationChannel, NotificationLog, PanelSetting, MessageLog 保持不变) ...

class ApiKey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    exchange: str
    api_key: str  # Encrypted
    secret_key: Optional[str] = Field(default=None) # Encrypted
    passphrase: Optional[str] = Field(default=None) # Encrypted
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StrategyProject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    project_path: str
    config_path: str
    tags: Optional[str] = Field(default="")
    description: Optional[str] = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    instances: List["Instance"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class Instance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    mode: str
    status: str = Field(default="stopped")
    # --- 修改: pid 现在是字符串，可以存储进程ID或容器ID ---
    pid: Optional[str] = Field(default=None)
    start_time: Optional[datetime] = Field(default=None)
    stop_time: Optional[datetime] = Field(default=None)
    log_path: Optional[str] = Field(default=None)
    
    # --- 新增: 记录实例的运行方式 ---
    runner: str = Field(default="process") # 'process' or 'docker'

    project_id: int = Field(foreign_key="strategyproject.id")
    project: StrategyProject = Relationship(back_populates="instances")

    config_snapshot: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    @property
    def log_file_exists(self) -> bool:
        return Path(self.log_path).exists() if self.log_path else False

class NotificationChannel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    channel_type: str
    is_enabled: bool = Field(default=True)
    config_json: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    channel_id: int = Field(foreign_key="notificationchannel.id")
    channel_name: str
    message: str
    status: str
    details: Optional[str] = Field(default=None)

class PanelSetting(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str

class MessageLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    level: str
    source: str
    message: str

# --- 新增: 面板API密钥模型 ---
class PanelApiKey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    key_prefix: str = Field(unique=True)
    hashed_key: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = Field(default=None)