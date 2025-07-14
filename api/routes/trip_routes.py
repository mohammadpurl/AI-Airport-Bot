from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.database.database import get_db
from api.schemas.trip_schema import TripCreate, Trip
from api.services.trip_service import create_trip, get_trip

router = APIRouter()


@router.post("/trips/", response_model=Trip)
def create_trip_endpoint(trip: TripCreate, db: Session = Depends(get_db)):
    try:
        db_trip = create_trip(db, trip)
        return db_trip
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trips/{trip_id}", response_model=Trip)
def get_trip_endpoint(trip_id: str, db: Session = Depends(get_db)):
    db_trip = get_trip(db, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db_trip
