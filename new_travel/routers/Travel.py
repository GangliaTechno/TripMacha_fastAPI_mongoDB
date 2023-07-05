from models.Getmodel import Getmodel
from fastapi import APIRouter
import openai
import googlemaps
import json
from pprint import pprint
import datetime
import requests

travel_ml=APIRouter()

openai.api_key = "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"
api_key_maps = "AIzaSyDMWSgHTmFD9UdPTYIvLkXww_eyRdI5ggA"
api_key = "AIzaSyDMWSgHTmFD9UdPTYIvLkXww_eyRdI5ggA"
gmaps = googlemaps.Client(key=api_key_maps)

def get_chatgpt_response(place, start_time, end_time, distance):
    messages = [{"role": "system", "content": "You are a intelligent assistant."}]
    template = f"I am in {place} with a {distance} travel radius, and I have {start_time} to {end_time} free. Please create an itinerary with activities and travel details, considering a buffer time of 20 minutes. Prioritize locations based on the shortest distance first. I want the itinerary to only travel on the road by car, no airways, no train included. Provide the output in JSON format with fields: Time, Location, Activity, Duration, Travel Time, Spend Time and Distance (in the specified order only).Give me only the itinerary, no other explanation or suggestion or sorry message or any alternatives"

    if template:
        messages.append(
            {"role": "user", "content": template},
        )
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    reply = chat.choices[0].message.content
    output = reply.split("```")[0]
    output = output.replace("\\n", "", 100)
    output = output.replace("json", "")
    output = output.replace("\\", "")
    output = output.lower()
    return output

def get_coordinates_from_place_id(api_key, place_id):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?place_id={place_id}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "OK":
        result = data["results"][0]
        latitude = result["geometry"]["location"]["lat"]
        longitude = result["geometry"]["location"]["lng"]
        return latitude, longitude
    else:
        return None

def is_place_open(place_id, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=opening_hours&key={api_key}"
    response = requests.get(url)
    data = response.json()
    current_datetime = datetime.datetime.now()
    current_day = current_datetime.weekday()
    current_time = current_datetime.strftime("%H:%M")
    time_available = False
    currently_open = False
    currently_closed = False
    time_open = "NA"
    time_close = "NA"

    # checking if opening hours data is available
    if data["result"] == {}:
        return {
            "time_available": time_available,
            "currently_open": currently_open,
            "currently_closed": currently_closed,
            "open_time": time_open,
            "close_time": time_close,
        }
    else:
        # opeimg hours data is available so loop through each day in to find current days open and close timings
        for period in data["result"]["opening_hours"]["periods"]:
            day = period["open"]["day"]
            open_time = period["open"]["time"]
            time_available = True
            # if close time not available handle the exception
            try:
                closse_time = period["close"]["time"]
            except:
                time_available = False
           
            # if closing time is available, the only we check for current days timings of a place
            if time_available is True:
                if day == current_day:
                    if open_time <= current_time <= closse_time:
                       currently_open = True
                    else:
                        currently_closed = True
                    time_close = closse_time
                    time_open = open_time

        return {
            "time_available": time_available,
            "currently_open": currently_open,
            "currently_closed": currently_closed,
            "open_time": time_open,
            "close_time": time_close,

        }

def without_itinerary(json_res):
    pass

def with_itinerary(json_res):
    places_output = []
    for place in json_res["itinerary"]:
        place_name = place["location"]

        # send request to GoogleMap API to find place using place name
        place_result = gmaps.find_place(
            input=place_name,
            input_type="textquery",
        )
        # after finding place, we extract placeID
        if place_result["status"] == "OK" and len(place_result["candidates"]) > 0:
            place_id = place_result["candidates"][0]["place_id"]

        # now we extract coordinates, based on placeID extracted above
        coordinates = get_coordinates_from_place_id(api_key, place_id)

        # if coordinates exists, store them in place object
        if coordinates:
            latitude, longitude = coordinates
            place["latitiude"] = latitude
            place["longitude"] = longitude
        else:
            place["latitiude"] = None
            place["longitude"] = None

        # print(place["location"])
        place_timing = is_place_open(place_id, api_key)
        place["timing"] = place_timing
        places_output.append(place)
    return places_output

def get_itinerary_plan(place, start_time, end_time, distance):
    output = get_chatgpt_response(
        place=place, start_time=start_time, end_time=end_time, distance=distance
    )

    if output.find("itinerary") == -1:
        get_itinerary_plan(
            place=place, start_time=start_time, end_time=end_time, distance=distance
        )
        # response = without_itinerary(json_out)
    else:
        try:
            json_out = json.loads(output)
            response = with_itinerary(json_out)
            json_data_str = json.dumps(response)
            x = json_data_str.replace("[", '{"plan":[', 1)
            x = x.replace("]", "]}", 1)
            json_output = json.loads(x)
            #pprint(json_output)
            return json_output
        except:
            error = {"message": "internall error"}
            print(error)
            return error

def generate_ml(place, start_time, end_time, distance):
    itinerary_list = []
    for _ in range(3):
        itinerary = get_itinerary_plan(place, start_time, end_time, distance)
        itinerary_list.append(itinerary)
    return itinerary_list

@travel_ml.post('/travelml')
async def getdetails(obj: Getmodel):
    # Call the generate_ml function to get the itinerary list
    itinerary_list = generate_ml(obj.place, obj.start_time, obj.end_time, obj.distance)
    #pprint(itinerary_list)
    new_itinerary_list = []

    for item in itinerary_list:
        pprint(item)
        itinerary_count = len(item['plan'])
        separated_item = {'count': itinerary_count, 'item': item}
        new_itinerary_list.append(separated_item)
        pprint('------------------------------------------------------')

    # Prepare the response data
    response_data = {
        'itinerary_list': new_itinerary_list,
        'itinerary_count': len(new_itinerary_list)
    }
    pprint(response_data)
    # Convert the data to JSON format
    json_data = json.dumps(response_data)
    # Return the JSON response
    return json_data