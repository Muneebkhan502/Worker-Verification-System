from pydantic import BaseModel, Field, model_validator
from datetime import date
from typing import Optional
from models import WorkerStatus
class WorkerBase(BaseModel):
    card_number: str
    name: str
    iqama_no: str
    company_name: str
    trade_course: str
    issued_date: date
    expiry_date: date
    status: WorkerStatus = WorkerStatus.active
    # we need to ensure expiry date issue date sy pihly na ho
    @model_validator(mode="after")
    def check_expiry_after_issued(self):
        if self.expiry_date <= self.issued_date:
            raise ValueError("Expiry date must be after issued date")
        return self

class WorkerCreate(WorkerBase):
    pass

class WorkerResponse(WorkerBase):
    id: int
    # tell fastapi to read from sqlalchemy model
    class Config:
        from_attribute = True

class WorkerUpdate(BaseModel):
    card_number: Optional[str] = None
    name: Optional[str] = None
    iqama_no: Optional[str] = None
    company_name: Optional[str] = None
    trade_course: Optional[str] = None
    issued_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: Optional[str] = None


    @model_validator(mode="after")
    def check_expiry_after_issued(self):
        if self.issued_date is not None and self.expiry_date is not None:
            if self.expiry_date <= self.issued_date:
                raise ValueError("Expiry date must be after issued date")
        return self