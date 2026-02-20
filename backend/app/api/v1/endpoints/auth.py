from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    SignupRequest, LoginRequest, TokenResponse, LoginStepResponse,
    TwoFASetupResponse, TwoFAEnableRequest, TwoFAVerifyLoginRequest,
)
from app.services.auth_service import signup, login_step, setup_2fa, enable_2fa, verify_2fa_login

router = APIRouter()


@router.post("/signup", response_model=TokenResponse)
async def signup_endpoint(payload: SignupRequest, db: AsyncSession = Depends(get_db)):
    user = await signup(db, payload.email, payload.full_name, payload.password)
    result = await login_step(db, payload.email, payload.password)
    return {"access_token": result["access_token"], "token_type": "bearer"}


@router.post("/login", response_model=LoginStepResponse)
async def login_endpoint(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await login_step(db, payload.email, payload.password)
    return result


@router.post("/2fa/setup", response_model=TwoFASetupResponse)
async def setup_2fa_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await setup_2fa(current_user, db)
    return result


@router.post("/2fa/enable")
async def enable_2fa_endpoint(
    payload: TwoFAEnableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await enable_2fa(current_user, payload.code, db)
    return {"enabled": True}


@router.post("/2fa/verify-login", response_model=TokenResponse)
async def verify_2fa_login_endpoint(payload: TwoFAVerifyLoginRequest, db: AsyncSession = Depends(get_db)):
    token = await verify_2fa_login(db, payload.temp_token, payload.code)
    return {"access_token": token, "token_type": "bearer"}
