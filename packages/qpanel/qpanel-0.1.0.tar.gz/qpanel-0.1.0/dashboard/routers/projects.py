# dashboard/routers/projects.py
import sys
import os
import importlib.util
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from fastapi import APIRouter, Request, Depends, Form, HTTPException, BackgroundTasks # <-- 修正: 添加 BackgroundTasks
from fastapi.responses import HTMLResponse, Response, JSONResponse
from sqlmodel import Session, select

from .. import models, security
from ..database import get_session
from ..shared import templates, SAFE_BASE_DIR, LOGS_DIR, PROJECTS_DIR
from .instances import _launch_instance_process, _handle_launch_exception
from ..logger_service import add_log # <-- 修正: 确保 add_log 已导入

router = APIRouter(tags=["projects"])

@router.get("/api/projects/all", response_class=JSONResponse)
def api_get_all_projects(session: Session = Depends(get_session)):
    projects = session.exec(select(models.StrategyProject)).all()
    project_list = [{"id": p.id, "name": p.name, "path": p.project_path} for p in projects]
    return JSONResponse(content=project_list)

def _get_strategy_class_from_project(project: models.StrategyProject):
    project_root = Path(project.project_path)
    config_path = project_root / project.config_path
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        spec = importlib.util.spec_from_file_location("config_module", config_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        strategy_class = getattr(config_module, 'STRATEGY_CLASS', None)
        if not strategy_class:
            raise AttributeError("STRATEGY_CLASS not found in config file.")
        return strategy_class
    finally:
        if str(project_root) in sys.path:
            sys.path.remove(str(project_root))

def _parse_dynamic_params(form_data: dict) -> dict:
    strategy_params = {}
    for key, value in form_data.items():
        if key.startswith("params:"):
            param_name = key.split(":", 1)[1]
            try:
                # Attempt to convert to float, then to int if it's a whole number
                float_val = float(value)
                if float_val.is_integer():
                    value = int(float_val)
                else:
                    value = float_val
            except (ValueError, TypeError):
                # Handle booleans and strings
                if isinstance(value, str):
                    if value.lower() == 'true': value = True
                    elif value.lower() == 'false': value = False
            strategy_params[param_name] = value
    return strategy_params

@router.post("/api/projects/from-ide", response_class=JSONResponse)
def api_create_project_from_ide(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    project_path: str = Form(...),
    config_path: str = Form(...), 
):
    p_path = Path(project_path)
    if not p_path.is_relative_to(PROJECTS_DIR):
        raise HTTPException(status_code=403, detail="Can only create projects within the managed projects directory.")
        
    if session.exec(select(models.StrategyProject).where(models.StrategyProject.project_path == project_path)).first():
        raise HTTPException(status_code=409, detail="A project for this directory already exists.")
    
    project_name = p_path.name
    
    if session.exec(select(models.StrategyProject).where(models.StrategyProject.name == project_name)).first():
        project_name = f"{project_name}-{os.urandom(2).hex()}"

    project = models.StrategyProject(
        name=project_name, 
        project_path=str(p_path),
        config_path=config_path,
        tags="IDE",
        description=f"Project created from IDE for directory '{p_path.name}'."
    )
    session.add(project)
    session.commit()
    
    add_log(session, "INFO", "Projects", f"Project '{project_name}' was created from IDE.", background_tasks)
    return JSONResponse(content={"status": "success", "message": f"Project '{project_name}' created!"})

# --- Page Rendering Routes ---
@router.get("/projects", response_class=HTMLResponse)
async def page_projects(request: Request):
    return templates.TemplateResponse("projects.html", {"request": request})

@router.get("/projects/{project_id}", response_class=HTMLResponse)
async def page_project_detail(project_id: int, request: Request, session: Session = Depends(get_session)):
    project = session.get(models.StrategyProject, project_id)
    if not project: raise HTTPException(404)
    api_keys = session.exec(select(models.ApiKey)).all()
    return templates.TemplateResponse("project_detail.html", {
        "request": request, "project": project, 
        "now_str": datetime.now().strftime('%Y%m%d-%H%M%S'), "api_keys": api_keys
    })

# --- Project Management API Routes ---
@router.get("/api/projects/list", response_class=HTMLResponse)
def api_get_projects_list(request: Request, session: Session = Depends(get_session), tags: str = ""):
    statement = select(models.StrategyProject).order_by(models.StrategyProject.name)
    if tags: statement = statement.where(models.StrategyProject.tags.contains(tags))
    projects = session.exec(statement).all()
    return templates.TemplateResponse("_projects_table.html", {"request": request, "projects": projects})

@router.post("/api/projects", response_class=Response)
def api_create_project(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session), name: str = Form(...), project_path: str = Form(...), 
    config_path: str = Form(...), tags: str = Form(""), description: str = Form(""),
):
    if session.exec(select(models.StrategyProject).where(models.StrategyProject.name == name)).first():
        return Response(content=f"<div class='alert alert-danger'>Project with name '{name}' already exists.</div>", status_code=409)
    
    p = Path(project_path)
    if not p.is_absolute():
        p = (SAFE_BASE_DIR / p).resolve()
    
    if not p.is_relative_to(SAFE_BASE_DIR):
        raise HTTPException(status_code=403, detail="Path must be within the safe directory.")

    project = models.StrategyProject(name=name, project_path=str(p), config_path=config_path, tags=tags, description=description)
    session.add(project)
    session.commit()
    
    add_log(session, "INFO", "Projects", f"Project '{name}' was created manually.", background_tasks)
    return Response(status_code=200, headers={"HX-Trigger": "projectAdded"})

@router.delete("/api/projects/{project_id}", response_class=Response)
def api_delete_project(
    project_id: int, 
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    project = session.get(models.StrategyProject, project_id)
    if not project: raise HTTPException(404)
    
    project_name = project.name
    session.delete(project)
    session.commit()

    add_log(session, "WARNING", "Projects", f"Project '{project_name}' and all its instances have been deleted.", background_tasks)
    return Response(status_code=200, headers={"HX-Trigger": "projectDeleted"})

@router.get("/api/projects/tags", response_class=HTMLResponse)
def api_get_tags(request: Request, session: Session = Depends(get_session)):
    projects = session.exec(select(models.StrategyProject)).all()
    all_tags = set(t.strip() for p in projects if p.tags for t in p.tags.split(',') if t.strip())
    return templates.TemplateResponse("_tags_filter.html", {"request": request, "tags": sorted(list(all_tags))})

@router.get("/api/projects/{project_id}/params", response_class=HTMLResponse)
async def api_get_strategy_params(project_id: int, request: Request, session: Session = Depends(get_session)):
    project = session.get(models.StrategyProject, project_id)
    if not project: raise HTTPException(404)
    try:
        strategy_class = _get_strategy_class_from_project(project)
        params = strategy_class.describe_params()
        return templates.TemplateResponse("_strategy_params_form.html", {"request": request, "params": params})
    except Exception as e:
        return templates.TemplateResponse("_strategy_params_form.html", {"request": request, "error": f"Failed to load params: {e}"})

# --- Instance-related API Routes (prefixed with /api/projects/{id}/...) ---
@router.get("/api/projects/{project_id}/instances", response_class=HTMLResponse)
async def api_get_instances_list(request: Request, project_id: int, mode: str, session: Session = Depends(get_session)):
    statement = select(models.Instance).where(models.Instance.project_id == project_id, models.Instance.mode == mode).order_by(models.Instance.id.desc())
    instances = session.exec(statement).all()
    template = "_live_instances_list.html" if mode == 'live' else "_backtest_history.html"
    return templates.TemplateResponse(template, {"request": request, "instances": instances})

@router.get("/api/projects/{project_id}/instances-options", response_class=HTMLResponse)
async def api_get_instances_options(request: Request, project_id: int, session: Session = Depends(get_session)):
    statement = select(models.Instance).order_by(models.Instance.id.desc()).where(models.Instance.project_id == project_id)
    instances = session.exec(statement).all()
    return templates.TemplateResponse("_instance_log_selector.html", {"request": request, "instances": instances})

@router.post("/api/projects/{project_id}/live/start", response_class=Response)
async def api_start_live_instance(
    project_id: int, 
    request: Request, 
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    run_in_docker: bool = Form(False)
):
    form_data = dict(await request.form())
    project = session.get(models.StrategyProject, project_id)
    if not project: raise HTTPException(404)
    
    api_key_id = form_data.get("api_key_id")
    if not api_key_id: raise HTTPException(400, "API Key is required for live instances.")
    api_key_record = session.get(models.ApiKey, int(api_key_id))
    if not api_key_record: raise HTTPException(404, "API Key not found.")
        
    engine_params = {
        "exchange_name": api_key_record.exchange,
        "api_key": security.decrypt_data(api_key_record.api_key),
        "secret_key": security.decrypt_data(api_key_record.secret_key),
        "passphrase": security.decrypt_data(api_key_record.passphrase),
    }
    
    instance_name = form_data.get("name")
    instance = models.Instance(name=instance_name, mode='live', status='starting', project_id=project_id)
    session.add(instance); session.commit(); session.refresh(instance)
    instance.log_path = str(LOGS_DIR / f"instance_{instance.id}.log"); session.commit()
    
    try:
        overrides = {
            "ENGINE_PARAMS": engine_params, 
            "STRATEGY_PARAMS": _parse_dynamic_params(form_data)
        }
        pid_or_cid = _launch_instance_process(instance, project, overrides, run_in_docker)
        instance.pid, instance.status, instance.start_time = pid_or_cid, 'running', datetime.utcnow()
        session.commit()
        add_log(session, "INFO", "Instances", f"Live instance '{instance_name}' (Project: {project.name}) was started.", background_tasks)
    except Exception as e:
        _handle_launch_exception(e, instance, session)
        add_log(session, "WARNING", "Instances", f"Failed to start live instance '{instance_name}': {e}", background_tasks)
        
    return Response(status_code=200, headers={"HX-Trigger": "instanceUpdated"})

@router.post("/api/projects/{project_id}/backtest", response_class=HTMLResponse)
async def api_run_backtest(
    project_id: int, 
    request: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    run_in_docker: bool = Form(False)
):
    form_data = dict(await request.form())
    project = session.get(models.StrategyProject, project_id)
    if not project: raise HTTPException(404)
    
    instance_name = form_data.get("name")
    instance = models.Instance(name=instance_name, mode='backtest', status='starting', project_id=project_id)
    session.add(instance); session.commit(); session.refresh(instance)
    instance.log_path = str(LOGS_DIR / f"instance_{instance.id}.log"); session.commit()
    
    try:
        overrides = {
            "BACKTEST_PARAMS": {"data_path": form_data.get("data_path"), "initial_cash": float(form_data.get("initial_cash", 10000))},
            "STRATEGY_PARAMS": _parse_dynamic_params(form_data)
        }
        pid_or_cid = _launch_instance_process(instance, project, overrides, run_in_docker)
        instance.pid, instance.status, instance.start_time = pid_or_cid, 'running', datetime.utcnow()
        session.commit()
        add_log(session, "INFO", "Instances", f"Backtest instance '{instance_name}' (Project: {project.name}) was started.", background_tasks)
    except Exception as e:
        _handle_launch_exception(e, instance, session)
        add_log(session, "WARNING", "Instances", f"Failed to start backtest '{instance_name}': {e}", background_tasks)
    
    context = {"request": request, "instance": instance, "cpu_percent": 0.0, "memory_mb": 0.0}
    return templates.TemplateResponse("_backtest_item.html", context, headers={"HX-Trigger": "backtestUpdated"})