from pydantic import BaseModel

class TravelDetails(BaseModel):
    Time: str
    Location: str
    Activity: str
    Duration: str
    TravelTime: str
    Distance: str
