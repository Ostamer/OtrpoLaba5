from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import os

SECRET_KEY = os.getenv("SECRET_KEY", "default_fallback_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Время жизни токена

# Фиксированный токен
UNIVERSAL_TOKEN = "SUPERAUTHTOKEN"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="fake-url")

# Проверка токена
def verify_token(token: str = Depends(oauth2_scheme)):
    print(f"Received token: {token}")
    if token != UNIVERSAL_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"sub": "user"}
