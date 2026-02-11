from typing import Any
from pydantic import BaseModel, model_validator
from fastapi.encoders import jsonable_encoder


class ApiResponse(BaseModel):
    success: bool = True
    message: str = "ok"
    data: Any = None

    @model_validator(mode="before")
    @classmethod
    def encode_data(cls, values: Any):
        if isinstance(values, dict) and "data" in values:
            values["data"] = jsonable_encoder(values.get("data"))
        return values
