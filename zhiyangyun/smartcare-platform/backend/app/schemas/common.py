from pydantic import BaseModel
from typing import Any


class ApiResp(BaseModel):
    success: bool = True
    message: str = "ok"
    data: Any = None
