from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from datetime import date
from sqlalchemy import Enum as SQLEnum
import enum

class WorkerStatus(str, enum.Enum):
    active = "active",
    suspended = "suspended",
    cancelled = "cancelled"

    def __str__(self):
        return self.value
class Worker(Base):
    __tablename__ = "workers"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    card_number: Mapped[str] = mapped_column(unique=True, index=True)
    iqama_no: Mapped[str] = mapped_column(unique=True, index=True)
    company_name: Mapped[str]
    trade_course: Mapped[str]
    issued_date: Mapped[date]
    expiry_date: Mapped[date]
    status: Mapped[WorkerStatus] = mapped_column(SQLEnum(WorkerStatus), default=WorkerStatus.active, nullable=False)


    @property
    def is_expired(self) -> bool:
        return self.expiry_date < date.today()

    @property
    def display_status(self) -> str:
        if self.is_expired:
            return "expired"
        return self.status.value
