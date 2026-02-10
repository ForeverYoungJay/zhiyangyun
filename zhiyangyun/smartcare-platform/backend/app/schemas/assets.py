from pydantic import BaseModel
from typing import Optional


class BuildingCreate(BaseModel):
    code: str
    name: str
    address: Optional[str] = None


class BuildingUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class FloorCreate(BaseModel):
    building_id: str
    floor_no: int
    name: Optional[str] = None


class FloorUpdate(BaseModel):
    floor_no: Optional[int] = None
    name: Optional[str] = None


class RoomCreate(BaseModel):
    building_id: str
    floor_id: str
    room_no: str
    room_type: Optional[str] = None
    capacity: int = 1


class RoomUpdate(BaseModel):
    room_no: Optional[str] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[str] = None


class BedCreate(BaseModel):
    room_id: str
    bed_no: str
    status: str = "vacant"


class BedUpdate(BaseModel):
    bed_no: Optional[str] = None
    status: Optional[str] = None


class BedStatusReq(BaseModel):
    status: str
