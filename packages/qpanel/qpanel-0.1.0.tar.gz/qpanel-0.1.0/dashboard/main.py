# dashboard/main.py
import uvicorn
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import database
from .shared import ROOT_DIR, SAFE_BASE_DIR
# --- 改动: 导入新的 router ---
from .routers import dashboard, data, instances, projects, settings, files, market, developer, notifications
from .routers import docker, api_management # <-- 新增
from .auth_middleware import AuthMiddleware

# --- FastAPI App Initialization ---
app = FastAPI(title="Qpanel")
app.add_middleware(AuthMiddleware)
@app.on_event("startup")
def on_startup():
    """Initialize the database and tables on application startup."""
    database.create_db_and_tables()

# --- Static Files ---
app.mount("/static", StaticFiles(directory=ROOT_DIR / "static"), name="static")
app.mount("/reports", StaticFiles(directory=ROOT_DIR / "reports"), name="reports")
app.mount("/market_data", StaticFiles(directory=ROOT_DIR / "market_data"), name="market_data")

# --- Include Routers ---
app.include_router(dashboard.router)
app.include_router(data.router)
app.include_router(instances.router)
app.include_router(projects.router)
app.include_router(settings.router)
app.include_router(files.router)
app.include_router(market.router)
app.include_router(developer.router)
app.include_router(notifications.router)
app.include_router(docker.router) # <-- 新增
app.include_router(api_management.router) # <-- 新增

# ====================================================================
# Server Runner
# ====================================================================
def run_server():
    """Starts the Uvicorn server."""
    print("--- Q ---")
    print(f"INFO:     Listening on http://127.0.0.1:8000")
    print(f"INFO:     File browser safe root: {SAFE_BASE_DIR}")
    print(f"INFO:     Using Python executable: {sys.executable}")
    uvicorn.run(f"{__name__}:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    run_server()