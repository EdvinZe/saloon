from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import register_routers
from app.core.config import get_cors_allowed_origins
from app.core.init_db import init_db
from app.core.logging import setup_logging

setup_logging(debug=True)

app = FastAPI(title="Saloon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
register_routers(app)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
