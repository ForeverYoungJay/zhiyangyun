from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, asset, elder, care
from app.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(asset.router, prefix=settings.api_prefix)
app.include_router(elder.router, prefix=settings.api_prefix)
app.include_router(care.router, prefix=settings.api_prefix)


@app.get("/health")
def health():
    return {"success": True, "message": "ok", "data": {"status": "up"}}
