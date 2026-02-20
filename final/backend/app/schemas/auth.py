from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginStepResponse(BaseModel):
    mfa_required: bool
    access_token: str | None = None
    temp_token: str | None = None


class TwoFAEnableRequest(BaseModel):
    code: str = Field(min_length=6, max_length=8)


class TwoFAVerifyLoginRequest(BaseModel):
    temp_token: str
    code: str = Field(min_length=6, max_length=8)


class TwoFASetupResponse(BaseModel):
    secret: str
    otpauth_uri: str
    qr_image_data_url: str
