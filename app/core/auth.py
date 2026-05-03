import functools
from typing import Annotated
import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jws, jwt, ExpiredSignatureError, JWTError, JWSError
from jose.exceptions import JWKError, JWTClaimsError
from pydantic import BaseModel

from app.core.config import config

security = HTTPBearer()


class UserClaims(BaseModel):
    sub: str


@functools.lru_cache(maxsize=1)
def _fetch_jwks():
    return requests.get(config.jwks_uri, timeout=5).json()["keys"]


def find_public_key(kid: str):
    for key in _fetch_jwks():
        if key["kid"] == kid:
            return key
    return None


def validate_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    try:
        unverified_header = jws.get_unverified_header(credentials.credentials)
        public_key = find_public_key(unverified_header["kid"])
        token_payload = jwt.decode(
            token=credentials.credentials, key=public_key, algorithms="RS256"
        )
        return UserClaims(sub=token_payload["sub"])

    except (
        ExpiredSignatureError,
        JWTError,
        JWTClaimsError,
        JWSError,
        JWKError,
    ) as err:
        raise HTTPException(status_code=401, detail=str(err)) from err
