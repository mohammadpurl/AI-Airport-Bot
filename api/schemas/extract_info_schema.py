from pydantic import BaseModel
from typing import List


class Passenger(BaseModel):
    fullName: str
    nationalId: str
    luggageCount: int


class ExtractInfoRequest(BaseModel):
    messages: list[dict]  # [{"sender": str, "content": str}]


class ExtractInfoResponse(BaseModel):
    airportName: str
    travelDate: str
    flightNumber: str
    passengers: List[Passenger]
