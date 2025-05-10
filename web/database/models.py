from sqlalchemy import Column, Integer, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import datetime
from . import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    start_ts = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    end_ts = Column(DateTime, nullable=True)
    readings = relationship(
        "Reading",
        back_populates="session",
        cascade="all, delete-orphan"
    )


class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    ts = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    weed_pct = Column(Float, nullable=False)
    broken_pct = Column(Float, nullable=False)

    session = relationship("Session", back_populates="readings")
