from fastapi import FastAPI

from app.api.prospects import router as prospects_router
from app.api.site_audits import router as site_audits_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.2.0")
app.include_router(prospects_router)
app.include_router(site_audits_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
