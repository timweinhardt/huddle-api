from fastapi import FastAPI
from mangum import Mangum

from app.api.v1 import posts, memberships, users
from app.core.logging import setup_logging
from app.core.config import config

setup_logging()

app = FastAPI(title=config.app_name)
handler = Mangum(app)

# Routes
app.include_router(users.router, prefix="/api/v1")
app.include_router(memberships.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")