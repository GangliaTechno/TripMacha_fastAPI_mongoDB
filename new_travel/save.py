from fastapi import APIRouter
from models.SaveModel import SaveModel
from database.usermodel import ucol,savecol

save_rout=APIRouter()

@save_rout.post("/save")
def process_data(data: SaveModel):
    trip_data = data.save.dict()
    trip_id = savecol.insert_one(trip_data).inserted_id

    # Find the user in the user collection and add the trip ID to the saved key array
    user = ucol.find_one({"uid": data.uid})
    if user is None:
        return "No user"
    saved_trips = user.get("saved", [])
    saved_trips.append(trip_id)
    ucol.update_one({"uid": data.uid}, {"$set": {"saved": saved_trips}})

    # Return the trip ID
    return {"trip_id": str(trip_id)}