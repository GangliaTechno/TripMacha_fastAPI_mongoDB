from typing import List
from pydantic import BaseModel
from fastapi import APIRouter
from models.Getmodel import Getmodel
from models.TravelDetails import TravelDetails
from database.guestmodel import col

user_rout = APIRouter()

class TravelDetailsResponse(BaseModel):
    data: List[TravelDetails]

@user_rout.post("/getuser", response_model=TravelDetailsResponse)
async def getdetails(obj: Getmodel):
    result = ml(obj)
    response = TravelDetailsResponse(data=result)
    return response

def ml(data: Getmodel):
    abc = col.find()
    # Process abc and convert it into a list of TravelDetails instances
    result = []
    for item in abc:
        travel_details = TravelDetails(
            Time=item["Time"],
            Location=item["Location"],
            Activity=item["Activity"],
            Duration=item["Duration"],
            TravelTime=item["TravelTime"],
            Distance=item["Distance"]
        )
        result.append(travel_details)
    return result
