from pydantic import BaseModel

class Getmodel(BaseModel):
    from_location: str
    to_location: str
    radius: int
    location: str
    date: str
