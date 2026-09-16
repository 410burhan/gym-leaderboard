"""
This project's Supabase instance issues JWTs signed with an asymmetric key
(ES256), not the older shared-secret (HS256) approach. That means there's no
single secret to verify against - instead, Supabase publishes a public key
at a well-known JWKS (JSON Web Key Set) URL, and we verify each token's
signature against that public key. The private key that actually signs
tokens never leaves Supabase's servers, which is the whole point of
asymmetric signing: we can verify without ever holding anything secret.
"""
import time

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.config import settings

bearer_scheme = HTTPBearer()

_JWKS_URL = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
_JWKS_CACHE_TTL_SECONDS = 3600
_jwks_cache: dict = {"keys": [], "fetched_at": 0.0}


def _get_jwks(force_refresh: bool = False) -> list[dict]:
    now = time.time()
    stale = now - _jwks_cache["fetched_at"] > _JWKS_CACHE_TTL_SECONDS
    if force_refresh or not _jwks_cache["keys"] or stale:
        resp = httpx.get(_JWKS_URL, timeout=5)
        resp.raise_for_status()
        _jwks_cache["keys"] = resp.json()["keys"]
        _jwks_cache["fetched_at"] = now
    return _jwks_cache["keys"]


def _find_signing_key(token: str) -> dict:
    kid = jwt.get_unverified_header(token).get("kid")

    for key in _get_jwks():
        if key.get("kid") == kid:
            return key

    # Key wasn't in our cache - Supabase may have rotated keys since we last
    # fetched. Force one refresh before giving up, rather than staying stale.
    for key in _get_jwks(force_refresh=True):
        if key.get("kid") == kid:
            return key

    raise JWTError(f"No matching signing key found for kid={kid}")


class CurrentUser:
    def __init__(self, user_id: str, email: str | None):
        self.user_id = user_id
        self.email = email


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    token = credentials.credentials
    try:
        signing_key = _find_signing_key(token)
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[signing_key.get("alg", "ES256")],
            audience="authenticated",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    return CurrentUser(user_id=user_id, email=payload.get("email"))
