from pymongo import MongoClient
from pymongo.database import Database
import os

# Injected automatically in monday production environments.
# For local dev: MNDY_MONGODB_CONNECTION_STRING=mongodb://localhost:27017/index_test
MONGO_URI = os.environ.get(
    "MNDY_MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/index_test"
)

client: MongoClient = None
db: Database = None
