from pydantic import BaseModel


class LoginReq(BaseModel):
    username: str
    password: str


class LoginUser(BaseModel):
    id: str
    username: str
    real_name: str
    tenant_id: str


class LoginData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUser
