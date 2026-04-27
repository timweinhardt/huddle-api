from fastapi import FastAPI
from mangum import Mangum

from app.api.v1 import posts
from app.core.logging import setup_logging
from app.core.config import config

setup_logging()

app = FastAPI(title=config.app_name)
handler = Mangum(app)

# Routes
app.include_router(posts.router, prefix="/api/v1")