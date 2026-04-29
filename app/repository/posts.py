from app.core.config import config
from app.db import Table

class PostRepository:
    def __init__(self):
        self.db = Table(config.posts_table_name, config.aws_region)