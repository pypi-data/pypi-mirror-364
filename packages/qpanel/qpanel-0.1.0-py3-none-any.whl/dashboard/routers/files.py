# dashboard/routers/files.py
import os
import json
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Query, Body
from fastapi.responses import HTMLResponse, JSONResponse

from ..shared import templates, SAFE_BASE_DIR # <-- 不再需要 PROJECTS_DIR

router = APIRouter(prefix="/api/files", tags=["files"])

def _is_path_in_safe_area(path: Path) -> bool:
    """
    CRITICAL SECURITY CHECK:
    Checks if a resolved path is within the configured SAFE_BASE_DIR.
    """
    try:
        # Resolve the path to get its absolute canonical path, preventing '..' attacks
        resolved_path = path.resolve()
        # Check if the resolved path is a sub-path of the safe directory
        resolved_path.relative_to(SAFE_BASE_DIR.resolve())
        return True
    except (ValueError, FileNotFoundError):
        # Also allow the safe directory itself
        return resolved_path == SAFE_BASE_DIR.resolve()

def _scan_dir(path: Path):
    # ... (此函数无需修改) ...
    items = []
    try:
        for entry in os.scandir(path):
            if entry.name.startswith('.') or entry.name == '__pycache__':
                continue
            item = {"name": entry.name, "path": entry.path}
            if entry.is_dir():
                item["type"] = "directory"
                item["children"] = _scan_dir(Path(entry.path))
            else:
                item["type"] = "file"
            items.append(item)
    except FileNotFoundError:
        return []
    items.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
    return items


@router.get("/tree", response_class=JSONResponse)
async def get_files_tree(path: str = Query(None)):
    if not path:
        return JSONResponse(content={
            "name": "No Project Selected", "type": "directory", "children": []
        })

    project_path = Path(path)
    # 使用新的、更宽松的安全检查
    if not _is_path_in_safe_area(project_path):
        raise HTTPException(status_code=403, detail="Access to this path is forbidden.")

    tree = _scan_dir(project_path)
    root_node = {
        "name": project_path.name,
        "path": str(project_path),
        "type": "directory",
        "children": tree,
        "open": True 
    }
    return JSONResponse(content=root_node)

@router.get("/content", response_class=JSONResponse)
async def get_file_content(path: str = Query(...)):
    if path == 'undefined': # 增加对前端错误的明确处理
        raise HTTPException(status_code=400, detail="Invalid path: undefined.")

    file_path = Path(path)
    if not _is_path_in_safe_area(file_path):
        raise HTTPException(status_code=403, detail="Access denied: Path is outside the allowed project directory.")
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found or is a directory.")
        
    try:
        content = file_path.read_text(encoding='utf-8')
        return JSONResponse(content={"path": path, "content": content})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")

@router.post("/content", response_class=JSONResponse)
async def save_file_content(payload: dict = Body(...)):
    path = payload.get("path")
    content = payload.get("content")
    if not path or content is None:
        raise HTTPException(status_code=400, detail="Invalid payload.")
        
    file_path = Path(path)
    if not _is_path_in_safe_area(file_path):
        raise HTTPException(status_code=403, detail="Access denied: Path is outside the allowed project directory.")
    
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        return JSONResponse(content={"status": "success", "message": f"File '{file_path.name}' saved successfully."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {e}")

# ... (旧的 /browse 函数保持不变, 但它也应该使用新的安全检查)
@router.get("/browse", response_class=HTMLResponse)
def browse_files(request: Request, path: str = Query(""), selectionType: str = Query("file")):
    try:
        current_path = SAFE_BASE_DIR if not path else Path(path)
        if not _is_path_in_safe_area(current_path):
             current_path = SAFE_BASE_DIR

        parent_path = None
        if current_path.resolve() != SAFE_BASE_DIR.resolve():
            parent_path = current_path.parent
            if not _is_path_in_safe_area(parent_path):
                parent_path = SAFE_BASE_DIR
        # ... (rest of the function is the same)
        items = []
        for entry in os.scandir(current_path):
            if entry.name.startswith('.'):
                continue
            
            if selectionType == 'dir' and not entry.is_dir():
                continue

            items.append({
                "name": entry.name,
                "path": os.path.join(current_path, entry.name),
                "type": "dir" if entry.is_dir() else "file"
            })

        items.sort(key=lambda x: (x['type'] != 'dir', x['name'].lower()))

        context = {
            "request": request,
            "items": items,
            "current_path": str(current_path),
            "parent_path": str(parent_path) if parent_path else None
        }
        return templates.TemplateResponse("_file_browser.html", context)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while browsing files.")