from fastapi import FastAPI
from app.api.system import router as system_router
from app.api.elders import router as elders_router

app = FastAPI(title="SmartCare API", version="0.1.0")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


app.include_router(system_router)
app.include_router(elders_router)
