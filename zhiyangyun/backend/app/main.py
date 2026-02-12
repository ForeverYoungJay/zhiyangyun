from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, asset, elder, care, m4_medication, m5_meal, m6_health, m7_billing, oa1_shift, oa2_approval, oa3_notification, oa4_training, b1_miniapp, b2_family, b3_dashboard, commerce
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
app.include_router(m4_medication.router, prefix=settings.api_prefix)
app.include_router(m5_meal.router, prefix=settings.api_prefix)
app.include_router(m6_health.router, prefix=settings.api_prefix)
app.include_router(m7_billing.router, prefix=settings.api_prefix)
app.include_router(oa1_shift.router, prefix=settings.api_prefix)
app.include_router(oa2_approval.router, prefix=settings.api_prefix)
app.include_router(oa3_notification.router, prefix=settings.api_prefix)
app.include_router(oa4_training.router, prefix=settings.api_prefix)
app.include_router(b1_miniapp.router, prefix=settings.api_prefix)
app.include_router(b2_family.router, prefix=settings.api_prefix)
app.include_router(b3_dashboard.router, prefix=settings.api_prefix)
app.include_router(commerce.router, prefix=settings.api_prefix)


@app.get("/health")
def health():
    return {"success": True, "message": "ok", "data": {"status": "up"}}
