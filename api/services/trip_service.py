from sqlalchemy.orm import Session
from typing import List, Optional
from api.models.trip_model import Trip, Passenger
from api.schemas.trip_schema import TripCreate


def create_trip(db: Session, trip_data: TripCreate) -> Trip:
    db_trip = Trip(
        airport_name=trip_data.airportName,
        travel_date=trip_data.travelDate,
        flight_number=trip_data.flightNumber,
    )
    db.add(db_trip)
    db.flush()  # تا trip_id برای مسافران داشته باشیم
    for p in trip_data.passengers:
        db_passenger = Passenger(
            trip_id=db_trip.id,
            full_name=p.fullName,
            national_id=p.nationalId,
            luggage_count=p.luggageCount,
        )
        db.add(db_passenger)
    db.commit()
    db.refresh(db_trip)
    return db_trip


def get_trip(db: Session, trip_id: str) -> Optional[Trip]:
    return db.query(Trip).filter(Trip.id == trip_id).first()
