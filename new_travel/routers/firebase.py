from fastapi import FastAPI,APIRouter
from firebase_admin import auth

firebase_api_router= APIRouter()

@firebase_api_router.get("/userinfo/{firebase_id}")
def get_user(firebase_id: str):
    #try:
        print("its executing")
        user = auth.get_user(firebase_id)
        json_data = {
            'uid': user.uid,
            'email': user.email,
            'display_name': user.display_name,
            'photo':user.photo_url,
            'phone_no':user.phone_number}
        return json_data