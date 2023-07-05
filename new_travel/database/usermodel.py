from pymongo import MongoClient

uri = "mongodb+srv://hackathonannova:hackathon4321@travels.ybxuj3u.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)

db = client["travels"]
ucol=db["user"]
savecol=db["plan1"]