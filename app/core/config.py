import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Config(BaseSettings):
    app_name: str = "Huddle"
    debug: bool = False
    cognito_region: str = os.getenv("COGNITO_REGION")
    cognito_user_pool_id: str = os.getenv("COGNITO_USER_POOL_ID")

    @property
    def jwks_uri(self):
        return f"https://cognito-idp.{self.cognito_region}.amazonaws.com/{self.cognito_user_pool_id}/.well-known/jwks.json"


config = Config()