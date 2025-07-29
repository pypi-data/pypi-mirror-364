# dashboard/routers/developer.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..shared import templates, PROJECTS_DIR # <-- 修改

router = APIRouter(tags=["developer"])

@router.get("/developer", response_class=HTMLResponse)
async def page_developer_ide(request: Request):
    """Renders the main developer IDE page."""
    context = {
        "request": request,
        "PROJ_DIR_STR": str(PROJECTS_DIR) # <-- 新增
    }
    return templates.TemplateResponse("developer_ide.html", context)