# dashboard/routers/market.py
import subprocess
import asyncio
import base64
from pathlib import Path
from fastapi import APIRouter, Request, Form, BackgroundTasks, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from ..shared import templates, PROJECTS_DIR, get_strategy_market_list
from ..logger_service import add_log
from ..database import get_session

router = APIRouter(tags=["market"])

def get_repo_name_from_url(url: str) -> str:
    return Path(url).stem

@router.get("/strategy-market", response_class=HTMLResponse)
async def page_strategy_market(request: Request):
    return templates.TemplateResponse("strategy_market.html", {"request": request})

@router.get("/api/market/list", response_class=HTMLResponse)
async def api_get_market_list(request: Request):
    # ... (no change)
    strategies = get_strategy_market_list()
    for strategy in strategies:
        repo_name = get_repo_name_from_url(strategy["repo_url"])
        strategy["clone_path"] = PROJECTS_DIR / repo_name
        strategy["is_cloned"] = strategy["clone_path"].exists()
        strategy["repo_id"] = base64.b64encode(repo_name.encode()).decode('utf-8').rstrip('=')
    return templates.TemplateResponse("_strategy_market_list.html", {"request": request, "strategies": strategies})

def _run_clone_task(repo_url: str, clone_path: Path):
    # ... (no change)
    try:
        process = subprocess.run(
            ["git", "clone", repo_url, str(clone_path)],
            capture_output=True, text=True, check=True
        )
        print(f"Successfully cloned {repo_url} to {clone_path}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to clone {repo_url}.")
        print(f"Stderr: {e.stderr}")
        if clone_path.exists():
            import shutil
            shutil.rmtree(clone_path)

@router.post("/api/market/clone", response_class=HTMLResponse)
async def api_clone_strategy(
    background_tasks: BackgroundTasks,
    repo_url: str = Form(...),
    session: Session = Depends(get_session)
):
    repo_name = get_repo_name_from_url(repo_url)
    clone_path = PROJECTS_DIR / repo_name
    repo_id = base64.b64encode(repo_name.encode()).decode('utf-8').rstrip('=')

    if clone_path.exists():
        raise HTTPException(status_code=400, detail="Repository already exists.")

    background_tasks.add_task(_run_clone_task, repo_url, clone_path)

    add_log(
        session, "INFO", "Strategy Market",
        f"Cloning strategy from repository '{repo_url}' into '{clone_path}'.",
        background_tasks
    )

    return HTMLResponse(f"""
        <div class="d-flex align-items-center text-muted">
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>
            Cloning...
        </div>
        <div hx-get="/api/market/status/{repo_id}" hx-trigger="every 2s" hx-swap="outerHTML"></div>
    """)

@router.get("/api/market/status/{repo_id}", response_class=HTMLResponse)
async def api_get_clone_status(repo_id: str):
    # ... (no change)
    repo_name = base64.b64decode(repo_id + '==').decode('utf-8')
    clone_path = PROJECTS_DIR / repo_name
    if clone_path.exists():
        return HTMLResponse("""
            <div class="d-flex align-items-center text-success">
                <i class="bi bi-check-circle-fill me-2"></i>
                Cloned
            </div>
        """)
    else:
        return HTMLResponse("")