from pymongo import AsyncMongoClient
from config import MONGODB_URI, DATABASE_NAME

client = AsyncMongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
destinations = db['destinations']
posts = db['posts']
deliveries = db['deliveries']