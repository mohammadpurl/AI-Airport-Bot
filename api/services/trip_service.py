from sqlalchemy.orm import Session
from typing import List, Optional
from api.models.trip_model import Trip, Passenger
from api.schemas.trip_schema import TripCreate


def create_trip(db: Session, trip_data: TripCreate) -> Trip:
    db_trip = Trip(
        airportName=trip_data.airportName,
        travelDate=trip_data.travelDate,
        flightNumber=trip_data.flightNumber,
    )
    db.add(db_trip)
    db.flush()  # تا trip_id برای مسافران داشته باشیم
    for p in trip_data.passengers:
        db_passenger = Passenger(
            trip_id=db_trip.id,
            name=p.name,
            lastName=p.lastName,
            nationalId=p.nationalId,
            passportNumber=p.passportNumber,
            luggageCount=p.luggageCount,
            passengerType=p.passengerType,
            gender=p.gender,
        )
        db.add(db_passenger)
    db.commit()
    db.refresh(db_trip)
    return db_trip


def get_trip(db: Session, trip_id: str) -> Optional[Trip]:
    return db.query(Trip).filter(Trip.id == trip_id).first()
