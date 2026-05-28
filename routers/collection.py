from fastapi import APIRouter, HTTPException
from pymongo.errors import CollectionInvalid
from pydantic import BaseModel

import database
from routers.index import router as index_router
from routers.document import router as document_router

router = APIRouter(prefix="/collection", tags=["collections"])
router.include_router(index_router, prefix="/{collection_name}")
router.include_router(document_router, prefix="/{collection_name}")


class CreateCollectionRequest(BaseModel):
    name: str


@router.get("")
def list_collections():
    return {"collections": database.db.list_collection_names()}


@router.post("", status_code=201)
def create_collection(body: CreateCollectionRequest):
    try:
        database.db.create_collection(body.name)
    except CollectionInvalid:
        raise HTTPException(status_code=409, detail=f"Collection '{body.name}' already exists")
    return {"created": body.name}


@router.delete("/{name}")
def delete_collection(name: str):
    database.db.drop_collection(name)
    return {"deleted": name}
