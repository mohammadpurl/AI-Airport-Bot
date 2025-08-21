from pydantic import BaseModel
from typing import List


class PassengerBase(BaseModel):
    name: str
    lastName: str
    nationalId: str
    passportNumber: str
    luggageCount: int
    passengerType: str
    gender: str


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
    travelType: str
    passengerCount: str
    additionalInfo: str = ""


class TripCreate(TripBase):
    passengers: List[PassengerCreate]


class Trip(TripBase):
    id: str
    passengers: List[Passenger]

    class Config:
        orm_mode = True
