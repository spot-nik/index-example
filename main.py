from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import MongoClient

import database
from routers import collection


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.client = MongoClient(database.MONGO_URI)
    database.db = database.client.get_default_database()
    yield
    database.client.close()


app = FastAPI(title="MongoDB Index Manager", lifespan=lifespan)

app.include_router(collection.router)
