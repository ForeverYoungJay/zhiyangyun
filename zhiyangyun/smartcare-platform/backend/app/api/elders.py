from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/elders", tags=["elders"])

_FAKE_DB = []


class ElderIn(BaseModel):
    name: str
    care_level: str = "L1"


class ElderOut(ElderIn):
    id: int


@router.get("", response_model=List[ElderOut])
async def list_elders():
    return _FAKE_DB


@router.post("", response_model=ElderOut)
async def create_elder(payload: ElderIn):
    row = {"id": len(_FAKE_DB) + 1, **payload.model_dump()}
    _FAKE_DB.append(row)
    return row
