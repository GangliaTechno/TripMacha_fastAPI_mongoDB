from fastapi import APIRouter
from config.database import feedback_collection
from models.SaveModel import FeedbackCollection
from bson import ObjectId
import pydantic
feedback_api_router=APIRouter()
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str
@feedback_api_router.post("/feedback")
def createFeedback(feedback: FeedbackCollection):
    data=feedback.dict()
    ins_feedback=feedback_collection.insert_one(data).inserted_id
    return {"message":"inserted feedback","feedback_id":ins_feedback}

