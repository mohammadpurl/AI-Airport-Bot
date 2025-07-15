from pydantic import BaseModel
from typing import List


class PassengerBase(BaseModel):
    fullName: str
    nationalId: str
    luggageCount: int


class PassengerCreate(PassengerBase):
    pass


class Passenger(PassengerBase):
    id: str

    class Config:
        orm_mode = True


class TripBase(BaseModel):
    airportName: str
    travelDate: str
    flightNumber: str


class TripCreate(TripBase):
    passengers: List[PassengerCreate]


class Trip(TripBase):
    id: str
    passengers: List[Passenger]

    class Config:
        orm_mode = True
