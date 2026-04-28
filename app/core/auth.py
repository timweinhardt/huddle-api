import requests
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jws, jwt, ExpiredSignatureError, JWTError, JWSError
from jose.exceptions import JWTClaimsError
from pydantic import BaseModel

from app.core.config import config

jwks = requests.get(config.jwks_uri).json()["keys"]
security = HTTPBearer()

class UserClaims(BaseModel):
    sub: str

def find_public_key(kid: str):
    for key in jwks:
        if key["kid"] == kid:
            return key
        
def validate_token(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    try:
        unverified_header = jws.get_unverified_header(credentials.credentials)
        public_key = find_public_key(unverified_header["kid"])
        token_payload = jwt.decode(
            token=credentials.credentials,
            key=public_key,
            algorithms="RS256"
        )
        return UserClaims(sub=token_payload["sub"])

    except (
        ExpiredSignatureError,
        JWTError,
        JWTClaimsError,
        JWSError,
    ) as error:
        raise HTTPException(status_code=401, detail=str(error))