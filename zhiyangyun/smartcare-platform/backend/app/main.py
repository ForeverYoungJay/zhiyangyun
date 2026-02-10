from fastapi import FastAPI
from app.api.system import router as system_router
from app.api.auth import router as auth_router
from app.api.assets import router as assets_router

app = FastAPI(title="SmartCare API", version="0.2.0")


@app.get("/healthz")
async def healthz():
    return {"success": True, "message": "ok", "data": {"status": "ok"}}


app.include_router(system_router)
app.include_router(auth_router)
app.include_router(assets_router)
