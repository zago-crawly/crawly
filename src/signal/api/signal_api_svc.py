import sys
from fastapi import APIRouter, Response, HTTPException

sys.path.append(".")
from src.signal.api.signal_api_svc_settings import SignalAPISettings
from src.common.api_svc import APISvc


class SignalAPI(APISvc):

    def __init__(self, settings: SignalAPISettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

    _outgoing_commands = {
        "read": "signal.read",
        "delete": "signal.delete"
    }

    async def create(self) -> None:
        pass

    async def read(self) -> dict:
        return await super().read(payload={"test": "ok"})
        
    async def delete(self, template_id: str) -> dict:
        return await super().delete(payload=template_id)
    
    async def update(self) -> None:
        pass

settings = SignalAPISettings()

app = SignalAPI(docs_url="/signals", root_path="/signals", redoc_url=None, settings=settings, title="Signal API service")

router = APIRouter(tags=['Signal'])


@router.post("/",
             status_code=405)
async def create():
    return HTTPException(405)

@router.get("/",
            status_code=200)
async def read():
    app._logger.error("Get signal")
    app.read()
    return

@router.delete("/{template_id}")
async def read(template_id: str):
    res = await app.delete(template_id)
    if res:
        return Response(status_code=204)
    return HTTPException(status_code=404)

@router.put("/",
            status_code=405)
async def update():
    return HTTPException(405)

app.include_router(router, prefix=f"/signals")
