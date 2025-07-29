# dashboard/routers/data.py
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List

from fastapi import APIRouter, Request, Depends, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, Response
from sqlmodel import Session

from ..shared import templates, MARKET_DATA_DIR
from ..logger_service import add_log
from ..database import get_session

router = APIRouter(tags=["data"])

def _run_download_task(exchange: str, symbol: str, timeframe: str, since: str):
    # This runs in a separate process, logging here might not be ideal.
    # The CLI command itself should do the logging.
    # However, we can log the *initiation* of the task.
    output_filename = f"{exchange}_{symbol.replace('/', '-')}_{timeframe}.csv"
    output_path = MARKET_DATA_DIR / output_filename
    command = [
        sys.executable, "-m", "eops.cli", "data", "download",
        exchange, symbol, timeframe, since, "--output", str(output_path)
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Download successful for {symbol}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Download failed for {symbol}.\nStderr: {e.stderr}")

def _get_local_data_files() -> List[dict]:
    # ... (no change)
    files_info = []
    for f in MARKET_DATA_DIR.glob('*.csv'):
        stat = f.stat()
        files_info.append({
            "name": f.name, "path": str(f.resolve()), "size_kb": f"{stat.st_size / 1024:.2f}",
            "modified_at": datetime.fromtimestamp(stat.st_mtime)})
    return sorted(files_info, key=lambda x: x['name'])

@router.get("/data-center", response_class=HTMLResponse)
async def page_data_center(request: Request):
    return templates.TemplateResponse("data_center.html", {"request": request})

@router.post("/api/data/download")
async def api_data_download(
    background_tasks: BackgroundTasks, 
    exchange: str = Form(...), 
    symbol: str = Form(...),
    timeframe: str = Form(...), 
    since: str = Form(...),
    session: Session = Depends(get_session)
):
    background_tasks.add_task(_run_download_task, exchange, symbol, timeframe, since)
    
    add_log(
        session, "INFO", "Data Center",
        f"Data download task started for {exchange}:{symbol} ({timeframe}) since {since}.",
        background_tasks
    )

    return HTMLResponse(
        "<div class='alert alert-success'>Download task started. The file list will refresh automatically.</div>",
        headers={"HX-Trigger": "dataFilesChanged"}
    )

@router.get("/api/data/list", response_class=HTMLResponse)
async def api_get_data_list(request: Request):
    files = _get_local_data_files()
    return templates.TemplateResponse("_data_files_table.html", {"request": request, "files": files})

@router.delete("/api/data/files/{filename}")
async def api_delete_data_file(
    filename: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    file_path = (MARKET_DATA_DIR / filename).resolve()
    if not file_path.is_relative_to(MARKET_DATA_DIR):
        raise HTTPException(status_code=403, detail="Forbidden")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path.unlink()
    
    add_log(
        session, "WARNING", "Data Center",
        f"Data file '{filename}' was deleted.",
        background_tasks
    )

    return Response(status_code=200, headers={"HX-Trigger": "dataFilesChanged"})

@router.get("/api/data/file-options", response_class=HTMLResponse)
async def api_get_data_files_as_options(request: Request):
    files = _get_local_data_files()
    return templates.TemplateResponse("_data_file_select.html", {"request": request, "files": files})