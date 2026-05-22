from fastapi import FastAPI

from app.api.router import register_routers
from app.core.init_db import init_db
from app.core.logging import setup_logging

setup_logging(debug=True)

app = FastAPI(title="Saloon API")

init_db()
register_routers(app)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
