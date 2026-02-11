from datetime import date
from pydantic import BaseModel, Field, field_validator


class LeadCreate(BaseModel):
    name: str
    phone: str
    source_channel: str = "unknown"
    notes: str = ""


class ElderCreate(BaseModel):
    lead_id: str | None = None
    elder_no: str = Field(min_length=1)
    name: str = Field(min_length=1)
    gender: str = "unknown"
    birth_date: date | None = None
    id_card: str = ""
    care_level: str = "L1"

    @field_validator("lead_id", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


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
