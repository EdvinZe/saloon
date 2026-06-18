import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import register_routers
from app.core.config import (
    get_cors_allowed_origins,
    get_max_request_body_bytes,
    should_auto_create_tables,
)
from app.core.init_db import init_db
from app.core.logging import setup_logging
from app.core.middleware import (
    RequestBodySizeLimitMiddleware,
    SecurityHeadersMiddleware,
)

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(title="Saloon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    RequestBodySizeLimitMiddleware,
    max_body_bytes=get_max_request_body_bytes(),
)
app.add_middleware(SecurityHeadersMiddleware)

if should_auto_create_tables():
    init_db()
else:
    logger.info("[STARTUP] Automatic table creation disabled")
register_routers(app)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
