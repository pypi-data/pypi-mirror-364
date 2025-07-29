# dashboard/routers/docker.py
import docker
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse

from ..shared import templates

router = APIRouter(tags=["docker"])

def get_docker_client():
    try:
        client = docker.from_env()
        client.ping()
        return client
    except Exception as e:
        return e

@router.get("/docker-center", response_class=HTMLResponse)
async def page_docker_center(request: Request):
    return templates.TemplateResponse("docker_center.html", {"request": request})

@router.get("/api/docker/status", response_class=HTMLResponse)
async def api_get_docker_status(request: Request):
    client = get_docker_client()
    context = {"request": request, "client": client}
    if isinstance(client, Exception):
        context["error"] = str(client)
        context["client"] = None
    else:
        context["info"] = client.info()
    return templates.TemplateResponse("_docker_status.html", context)

@router.post("/api/docker/build-image")
async def api_build_docker_image(background_tasks: BackgroundTasks):
    
    async def stream_build_logs():
        client = get_docker_client()
        if isinstance(client, Exception):
            yield f"data: <div class='text-danger'>Failed to connect to Docker: {client}</div>\n\n"
            return

        try:
            yield "data: <pre class='text-white bg-dark p-2 rounded' style='font-size: 0.8rem;'>\n"
            streamer = client.api.build(
                path=".", 
                dockerfile="Dockerfile", 
                tag="qpanel-runner:latest", 
                rm=True, 
                decode=True
            )
            for chunk in streamer:
                if 'stream' in chunk:
                    line = chunk['stream'].strip('\n')
                    yield f"data: {line}\n"
            yield "data: \n--- BUILD COMPLETE ---\n"
            yield "data: </pre>\n\n"
        except Exception as e:
            yield f"data: <div class='text-danger'>Build failed: {e}</div>\n\n"

    return StreamingResponse(stream_build_logs(), media_type="text/event-stream")