from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from api.database.database import Base
import uuid


class Trip(Base):  # type: ignore
    __tablename__ = "trips"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    airportName = Column(String, nullable=False)
    travelDate = Column(String, nullable=False)
    flightNumber = Column(String, nullable=False)
    passengers = relationship(
        "Passenger", back_populates="trip", cascade="all, delete-orphan"
    )


class Passenger(Base):  # type: ignore
    __tablename__ = "passengers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String, ForeignKey("trips.id"), nullable=False)
    fullName = Column(String, nullable=False)
    nationalId = Column(String, nullable=False)
    luggageCount = Column(Integer, nullable=False)
    trip = relationship("Trip", back_populates="passengers")
