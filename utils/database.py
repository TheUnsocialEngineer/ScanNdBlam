import os
from dotenv import load_dotenv
import pymongo

# Load environment variables from .env file
load_dotenv()

# Retrieve the MongoDB URI from the environment
mongodb_uri = os.getenv("MONGODB_URI")

# Create MongoDB client
myclient = pymongo.MongoClient(mongodb_uri)
mydb = myclient["Eoka"]
mycol = mydb["Servers bleeding"]

def add():
    print("")

def update():
    print("")