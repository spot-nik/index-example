from fastapi import APIRouter, HTTPException
from bson import ObjectId
from bson.errors import InvalidId

import database

router = APIRouter(prefix="/document", tags=["documents"])


def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


def _collection(collection_name: str):
    if collection_name not in database.db.list_collection_names():
        raise HTTPException(
            status_code=404, detail=f"Collection '{collection_name}' not found"
        )
    return database.db[collection_name]


@router.get("")
def list_documents(collection_name: str, limit: int = 100, skip: int = 0):
    col = _collection(collection_name)
    docs = [_serialize(doc) for doc in col.find().skip(skip).limit(limit)]
    return {"documents": docs}


@router.post("", status_code=201)
def create_document(collection_name: str, body: dict):
    col = _collection(collection_name)
    result = col.insert_one(body)
    return {"created": str(result.inserted_id)}


@router.delete("/{document_id}")
def delete_document(collection_name: str, document_id: str):
    col = _collection(collection_name)
    try:
        oid = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(
            status_code=400, detail=f"Invalid document id '{document_id}'"
        )
    result = col.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404, detail=f"Document '{document_id}' not found"
        )
    return {"deleted": document_id}
