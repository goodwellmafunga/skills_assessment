import pyotp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import hash_password, verify_password, create_token, decode_token
from app.core.config import settings
from app.utils.qr import qr_data_url


async def signup(db: AsyncSession, email: str, full_name: str, password: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        email=email,
        full_name=full_name,
        password_hash=hash_password(password),
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_step(db: AsyncSession, email: str, password: str) -> dict:
    result = await db.execute(select(User).where(User.email == email, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if user.totp_enabled:
        temp_token = create_token(str(user.id), settings.TEMP_TOKEN_EXPIRE_MINUTES, token_type="temp")
        return {"mfa_required": True, "temp_token": temp_token}

    access = create_token(str(user.id), settings.ACCESS_TOKEN_EXPIRE_MINUTES, token_type="access")
    return {"mfa_required": False, "access_token": access}


async def setup_2fa(user: User, db: AsyncSession) -> dict:
    if not user.totp_secret:
        user.totp_secret = pyotp.random_base32()
        user.totp_enabled = False
        await db.commit()
        await db.refresh(user)

    totp = pyotp.TOTP(user.totp_secret)
    uri = totp.provisioning_uri(name=user.email, issuer_name="SkillsAssessment")
    qr = qr_data_url(uri)

    return {
        "secret": user.totp_secret,
        "otpauth_uri": uri,
        "qr_image_data_url": qr,
    }


async def enable_2fa(user: User, code: str, db: AsyncSession) -> None:
    if not user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA not initialized")

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    user.totp_enabled = True
    await db.commit()


async def verify_2fa_login(db: AsyncSession, temp_token: str, code: str) -> str:
    try:
        payload = decode_token(temp_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid temp token")

    if payload.get("type") != "temp":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user or not user.totp_enabled or not user.totp_secret:
        raise HTTPException(status_code=401, detail="2FA not configured")

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid TOTP code")

    return create_token(str(user.id), settings.ACCESS_TOKEN_EXPIRE_MINUTES, token_type="access")
