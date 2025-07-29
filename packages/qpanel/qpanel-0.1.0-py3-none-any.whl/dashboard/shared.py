# dashboard/shared.py
import os
import json # <-- 已存在或新增
from pathlib import Path
from fastapi.templating import Jinja2Templates

# --- Core Application Configuration ---

# Base directories
ROOT_DIR = Path(__file__).parent.resolve()
SAFE_BASE_DIR = Path(os.getenv("EOPS_PANEL_SAFE_DIR", os.path.expanduser("~"))).resolve()
# --- 新增: 策略项目专用目录 ---
PROJECTS_DIR = SAFE_BASE_DIR / "eops_projects"
REPORTS_DIR = ROOT_DIR / "reports"
LOGS_DIR = ROOT_DIR / "logs"
TEMP_CONFIG_DIR = ROOT_DIR / "temp_configs"
MARKET_DATA_DIR = ROOT_DIR / "market_data"

# Ensure directories exist
PROJECTS_DIR.mkdir(exist_ok=True) # <-- 新增
REPORTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
TEMP_CONFIG_DIR.mkdir(exist_ok=True)
MARKET_DATA_DIR.mkdir(exist_ok=True)

# --- Shared Components ---

# Jinja2 Templates instance, shared across all routers
templates = Jinja2Templates(directory=ROOT_DIR / "templates")

# --- 新增: 添加自定义函数到 Jinja2 环境 ---
templates.env.globals['fromjson'] = json.loads


# --- 新增: 加载策略市场配置 ---
def get_strategy_market_list():
    market_file = ROOT_DIR / "market.json"
    if not market_file.exists():
        return []
    with open(market_file, 'r', encoding='utf-8') as f:
        return json.load(f)