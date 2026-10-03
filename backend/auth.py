from datetime import datetime, timedelta, timezone

from jose import jwt

# ============================================================
# AUTHENTICATION SETTINGS
# ============================================================

SECRET_KEY = "campusmind-secret-key-change-later"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ============================================================
# ADMIN ACCOUNT
# ============================================================

ADMIN_USERNAME = "admin"

ADMIN_PASSWORD = "admin123"


# ============================================================
# CREATE ACCESS TOKEN
# ============================================================

def create_access_token(username: str):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "role": "admin",
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token


# ============================================================
# VERIFY ACCESS TOKEN
# ============================================================

def verify_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return payload

    except Exception:

        return None