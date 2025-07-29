# dashboard/routers/dashboard.py
import psutil
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from .. import models
from ..database import get_session
from ..shared import templates

# FIX: Remove prefix, all paths will be absolute from the root
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def page_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/api/dashboard/stats", response_class=HTMLResponse)
def api_get_dashboard_stats(request: Request, session: Session = Depends(get_session)):
    running_instances = session.exec(select(models.Instance).where(models.Instance.status == 'running')).all()
    cpu_percent = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    context = {
        "request": request,
        "running_count": len(running_instances),
        "cpu_percent": cpu_percent,
        "mem_percent": mem.percent,
        "mem_total_gb": f"{mem.total / (1024**3):.2f}",
        "mem_used_gb": f"{mem.used / (1024**3):.2f}",
    }
    return templates.TemplateResponse("_dashboard_stats.html", context)