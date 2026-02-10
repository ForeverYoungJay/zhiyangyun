from pydantic import BaseModel


class BuildingCreate(BaseModel):
    name: str
    code: str


class FloorCreate(BaseModel):
    building_id: str
    floor_no: int
    name: str


class RoomCreate(BaseModel):
    building_id: str
    floor_id: str
    room_no: str
    room_type: str = "double"


class BedCreate(BaseModel):
    room_id: str
    bed_no: str


class BedUpdateStatus(BaseModel):
    status: str
