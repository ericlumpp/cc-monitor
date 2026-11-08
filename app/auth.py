import os
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)


def require_api_key(creds: HTTPAuthorizationCredentials | None = Depends(bearer)):
    key = os.environ.get("CC_MONITOR_API_KEY")
    if not key:
        raise HTTPException(503, "API key not configured")  # fail closed
    if creds is None or not secrets.compare_digest(creds.credentials.encode(), key.encode()):
        raise HTTPException(401, "invalid or missing API key", headers={"WWW-Authenticate": "Bearer"})