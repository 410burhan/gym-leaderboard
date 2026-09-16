"""
This is the actual 'authentication' layer. We don't issue or manage passwords
ourselves - Supabase Auth (a hosted identity provider) handles signup, login,
and issuing a signed JWT to the frontend. Our job as the backend is to verify
that JWT on every request and trust its claims. This is the standard pattern
used by real production APIs (Auth0, Cognito, Clerk, Supabase all work this way).
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.config import settings

bearer_scheme = HTTPBearer()


class CurrentUser:
    def __init__(self, user_id: str, email: str | None):
        self.user_id = user_id
        self.email = email


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    token = credentials.credentials
    try:
        # Supabase signs its JWTs with HS256 using the project's JWT secret.
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
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
