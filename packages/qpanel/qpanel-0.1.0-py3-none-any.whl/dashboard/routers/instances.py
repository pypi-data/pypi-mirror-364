# dashboard/routers/instances.py
import os
import sys
import psutil
import subprocess
import json
import docker
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlmodel import Session
from eops.utils.config_loader import build_final_config

from .. import models
from ..database import get_session
from ..shared import templates, LOGS_DIR, REPORTS_DIR, TEMP_CONFIG_DIR, PROJECTS_DIR, MARKET_DATA_DIR

router = APIRouter(prefix="/api/instances", tags=["instances"])

def _launch_instance_process(
    instance: models.Instance,
    project: models.StrategyProject,
    overrides: dict,
    run_in_docker: bool = False
) -> str:
    """
    Launches a strategy instance either as a local process or a Docker container.
    Returns the process ID or container ID as a string.
    """
    project_root = Path(project.project_path)
    if not project_root.is_dir():
        raise FileNotFoundError(f"Project root path does not exist: '{project_root}'")
    
    base_config_path = project_root / project.config_path
    if not base_config_path.is_file():
        raise FileNotFoundError(f"Base config file not found: '{base_config_path}'")

    log_file_path = LOGS_DIR / f"instance_{instance.id}.log"
    
    # --- Build Final Configuration ---
    overrides['MODE'] = instance.mode
    overrides['LOG_FILE'] = str(log_file_path) if not run_in_docker else f"/app/logs/instance_{instance.id}.log"
    overrides['PROJECT_ROOT'] = str(project_root) if not run_in_docker else f"/app/eops_projects/{project_root.name}"

    if instance.mode == 'backtest':
        report_dir = REPORTS_DIR / str(instance.id)
        report_dir.mkdir(exist_ok=True, parents=True)
        if 'BACKTEST_PARAMS' in overrides and 'data_path' in overrides['BACKTEST_PARAMS']:
            data_path = Path(overrides['BACKTEST_PARAMS']['data_path'])
            if run_in_docker:
                overrides['BACKTEST_PARAMS']['data_path'] = f"/app/market_data/{data_path.name}"
            else:
                overrides['BACKTEST_PARAMS']['data_path'] = str(data_path.as_posix())
        
    final_config = build_final_config(base_config_path, overrides)
    
    # --- Save Configuration Snapshot to Database ---
    strategy_class = final_config["STRATEGY_CLASS"]
    final_config_for_snapshot = final_config.copy()
    final_config_for_snapshot["STRATEGY_CLASS"] = f"{strategy_class.__module__}.{strategy_class.__name__}"
    
    if 'ENGINE_PARAMS' in final_config_for_snapshot:
        final_config_for_snapshot['ENGINE_PARAMS'].pop('api_key', None)
        final_config_for_snapshot['ENGINE_PARAMS'].pop('secret_key', None)
        final_config_for_snapshot['ENGINE_PARAMS'].pop('passphrase', None)
        
    instance.config_snapshot = final_config_for_snapshot
    instance.runner = 'docker' if run_in_docker else 'process'
    session = Session.object_session(instance)
    if session:
        session.add(instance)
        session.commit()
        session.refresh(instance)
    
    # --- Generate Temporary Python Config File ---
    temp_config_content = f"# Auto-generated wrapper for instance {instance.id}\n"
    temp_config_content += f"from pathlib import Path\n"
    if run_in_docker:
        temp_config_content += f"import sys\nsys.path.insert(0, '/app/eops_projects/{project_root.name}')\n"
    temp_config_content += f"from {base_config_path.stem} import *\n\n"
    
    config_to_write = final_config_for_snapshot.copy()
    config_to_write.pop("STRATEGY_CLASS", None)
    config_to_write.pop("PROJECT_ROOT", None)

    for key, value in config_to_write.items():
        if key in ["STRATEGY_PARAMS", "BACKTEST_PARAMS", "ENGINE_PARAMS"]:
            temp_config_content += f"if '{key}' in globals():\n"
            temp_config_content += f"    {key}.update({repr(value)})\n"
            temp_config_content += f"else:\n"
            temp_config_content += f"    {key} = {repr(value)}\n"

        else:
            temp_config_content += f"{key} = {repr(value)}\n"

    temp_config_path = TEMP_CONFIG_DIR / f"inst_{instance.id}_config.py"
    temp_config_path.write_text(temp_config_content, encoding='utf-8')

    # --- Launching Logic ---
    if run_in_docker:
        docker_client = docker.from_env()
        container_log_path = f"/app/logs/instance_{instance.id}.log"
        container_config_path = f"/app/temp_configs/{temp_config_path.name}"
        command = ["run", container_config_path, "--log-file", container_log_path]
        
        if instance.mode == 'backtest':
            container_report_dir = f"/app/reports/{instance.id}"
            command.extend(["--report-dir", container_report_dir])

        volumes = {
            str(PROJECTS_DIR.resolve()): {'bind': '/app/eops_projects', 'mode': 'ro'},
            str(TEMP_CONFIG_DIR.resolve()): {'bind': '/app/temp_configs', 'mode': 'ro'},
            str(LOGS_DIR.resolve()): {'bind': '/app/logs', 'mode': 'rw'},
            str(REPORTS_DIR.resolve()): {'bind': '/app/reports', 'mode': 'rw'},
            str(MARKET_DATA_DIR.resolve()): {'bind': '/app/market_data', 'mode': 'ro'},
        }

        container = docker_client.containers.run(
            "qpanel-runner:latest", command=command, volumes=volumes,
            labels={"qpanel.managed": "true", "qpanel.instance.id": str(instance.id)},
            detach=True, auto_remove=True, name=f"qpanel-inst-{instance.id}"
        )
        return container.short_id
    else:
        command = [sys.executable, "-m", "eops.cli", "run", str(temp_config_path), "--log-file", str(log_file_path)]
        if instance.mode == 'backtest':
            command.extend(["--report-dir", str(REPORTS_DIR / str(instance.id))])

        log_file_handle = open(log_file_path, 'w', encoding='utf-8')
        process = subprocess.Popen(command, cwd=project_root, stdout=log_file_handle, stderr=log_file_handle)
        return str(process.pid)

def _handle_launch_exception(e: Exception, instance: models.Instance, session: Session):
    instance.status = 'error'
    session.add(instance)
    session.commit()
    log_file = LOGS_DIR / f"instance_{instance.id}.log"
    log_file.parent.mkdir(exist_ok=True, parents=True)
    error_message = f"FATAL: Failed to launch instance process.\n\nError Type: {type(e).__name__}\n\nDetails: {e}"
    log_file.write_text(error_message, encoding='utf-8')
    print(error_message)


@router.get("/{instance_id}/status", response_class=HTMLResponse)
async def api_get_instance_status(request: Request, instance_id: int, session: Session = Depends(get_session)):
    instance = session.get(models.Instance, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    cpu_percent = 0.0
    memory_mb = 0.0
    
    if instance.status in ['running', 'starting'] and instance.pid:
        is_alive = False
        if instance.runner == 'process':
            if psutil.pid_exists(int(instance.pid)):
                try:
                    p = psutil.Process(int(instance.pid))
                    cpu_percent = p.cpu_percent(interval=None) 
                    memory_mb = p.memory_info().rss / (1024 * 1024)
                    is_alive = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    is_alive = False
            else:
                is_alive = False
        
        elif instance.runner == 'docker':
            try:
                docker_client = docker.from_env()
                container = docker_client.containers.get(instance.pid)
                stats = container.stats(stream=False)
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
                system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                online_cpus = stats['cpu_stats'].get('online_cpus', len(stats['cpu_stats']['cpu_usage']['percpu_usage']))
                if system_delta > 0 and cpu_delta > 0:
                    cpu_percent = (cpu_delta / system_delta) * online_cpus * 100.0
                memory_mb = stats['memory_stats']['usage'] / (1024 * 1024)
                is_alive = True
            except docker.errors.NotFound:
                is_alive = False
            except Exception:
                is_alive = True # Assume alive if stats fail, but container exists

        if not is_alive:
            report_file = REPORTS_DIR / str(instance.id) / "summary.txt"
            is_successful_backtest = (
                instance.mode == 'backtest' and 
                report_file.exists() and 
                "no trades" not in report_file.read_text(default="").lower() and
                "no returns" not in report_file.read_text(default="").lower()
            )
            instance.status = 'completed' if is_successful_backtest else 'error'
            instance.stop_time = datetime.utcnow()
            session.add(instance)
            session.commit()

    context = {"request": request, "instance": instance, "cpu_percent": cpu_percent, "memory_mb": memory_mb}
    template_name = "_live_instance_item.html" if instance.mode == 'live' else "_backtest_item.html"
    return templates.TemplateResponse(template_name, context)


@router.post("/{instance_id}/stop", response_class=Response)
async def api_stop_instance(instance_id: int, session: Session = Depends(get_session)):
    instance = session.get(models.Instance, instance_id)
    if instance and instance.status in ['running', 'starting'] and instance.pid:
        try:
            if instance.runner == 'process':
                if psutil.pid_exists(int(instance.pid)):
                    psutil.Process(int(instance.pid)).terminate()
            elif instance.runner == 'docker':
                docker_client = docker.from_env()
                docker_client.containers.get(instance.pid).stop(timeout=5)
            
            instance.status = 'stopped'
            instance.stop_time = datetime.utcnow()
        except (psutil.NoSuchProcess, docker.errors.NotFound) as e:
            instance.status = 'error' # Mark as error if it was already gone
            instance.stop_time = datetime.utcnow()
        
        session.add(instance)
        session.commit()
    return Response(status_code=200, headers={"HX-Trigger": "instanceUpdated"})


@router.get("/{instance_id}/logs", response_class=HTMLResponse)
def api_get_logs(instance_id: int, session: Session = Depends(get_session)):
    instance = session.get(models.Instance, instance_id)
    if not instance or not instance.log_path:
        return HTMLResponse("<div class='p-3 text-muted'>Log path not set for this instance.</div>")
    
    log_file = Path(instance.log_path)
    if not log_file.exists():
        return HTMLResponse(f"<div class='p-3 text-muted'>Log file not found at '{log_file}'. The process might have failed to start or is running in Docker.</div>")
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-200:]
        
        log_content = "".join(lines)
        import html
        escaped_content = html.escape(log_content)
        return HTMLResponse(f"<pre class='text-white bg-dark p-3' style='font-size: 0.8rem; border-radius: 4px;'>{escaped_content}</pre>")
    except Exception as e:
        return HTMLResponse(f"<div class='p-3 text-danger'>Error reading log file: {e}</div>")


@router.get("/{instance_id}/results", response_class=HTMLResponse)
async def api_get_instance_results(instance_id: int):
    report_dir = REPORTS_DIR / str(instance_id)
    summary_path = report_dir / "summary.txt"
    report_html_path = report_dir / "report.html"

    if not summary_path.exists():
        return HTMLResponse("<div class='alert alert-warning m-3'>Backtest results not found. The run may have failed or produced no trades.</div>")

    import html
    summary_text = html.escape(summary_path.read_text())
    
    html_content = f"""
    <div class="card mt-3">
        <div class="card-header"><h5 class="card-title mb-0">Performance Summary</h5></div>
        <div class="card-body"><pre style="white-space: pre-wrap;">{summary_text}</pre></div>
    </div>
    """
    if report_html_path.exists():
        html_content += f"""
        <div class="card mt-3">
            <div class="card-header"><h5 class="card-title mb-0">Full QuantStats Report</h5></div>
            <div class="card-body p-0" style="height: 850px; resize: vertical; overflow: hidden;">
                <iframe src="/reports/{instance_id}/report.html" width="100%" height="100%" 
                        style="border:0;">
                </iframe>
            </div>
        </div>
        """
    return HTMLResponse(content=html_content)