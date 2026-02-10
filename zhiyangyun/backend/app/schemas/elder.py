from datetime import date
from pydantic import BaseModel


class LeadCreate(BaseModel):
    name: str
    phone: str
    source_channel: str = "unknown"
    notes: str = ""


class ElderCreate(BaseModel):
    lead_id: str | None = None
    elder_no: str
    name: str
    gender: str = "unknown"
    birth_date: date | None = None
    id_card: str = ""
    care_level: str = "L1"


class ElderAdmit(BaseModel):
    building_id: str
    floor_id: str
    room_id: str
    bed_id: str
    admission_date: date


class ElderTransfer(BaseModel):
    building_id: str
    floor_id: str
    room_id: str
    bed_id: str


class ElderDischarge(BaseModel):
    discharge_date: date
    note: str = ""
