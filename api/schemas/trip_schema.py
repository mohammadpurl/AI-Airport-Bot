from pydantic import BaseModel, Field
from typing import List, Optional


class PassengerBase(BaseModel):
    fullName: str = Field(..., alias="full_name")
    nationalId: str = Field(..., alias="national_id")
    luggageCount: int = Field(..., alias="luggage_count")


class PassengerCreate(PassengerBase):
    pass


class Passenger(PassengerBase):
    id: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class TripBase(BaseModel):
    airportName: str = Field(..., alias="airport_name")
    travelDate: str = Field(..., alias="travel_date")
    flightNumber: str = Field(..., alias="flight_number")


class TripCreate(TripBase):
    passengers: List[PassengerCreate]


class Trip(TripBase):
    id: str
    passengers: List[Passenger]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
