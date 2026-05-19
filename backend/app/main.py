from fastapi import FastAPI

from app.modules.services.router import router as services_router

app = FastAPI(title="Saloon API")

app.include_router(
    services_router,
    prefix="/api/services",
    tags=["Services"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}