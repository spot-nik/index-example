from typing import Optional

from fastapi import APIRouter, HTTPException
from pymongo.errors import OperationFailure
from pydantic import BaseModel

import database

router = APIRouter(prefix="/index", tags=["indexes"])


class IndexField(BaseModel):
    field: str
    direction: int = 1  # 1 ascending, -1 descending


class CreateIndexRequest(BaseModel):
    fields: list[IndexField]
    name: Optional[str] = None
    unique: bool = False
    sparse: bool = False
    ttl: Optional[int] = None  # expireAfterSeconds; forces a single-field index
    partial_filter_expression: Optional[dict] = None


@router.get("")
def list_indexes(collection_name: str):
    if collection_name not in database.db.list_collection_names():
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    indexes = [dict(idx) for idx in database.db[collection_name].list_indexes()]
    return {"indexes": indexes}


@router.post("", status_code=201)
def create_index(collection_name: str, body: CreateIndexRequest):
    # Collections auto-create on first write in monday Document DB, so we allow
    # index creation even if the collection doesn't exist yet.

    if body.ttl is not None and len(body.fields) != 1:
        raise HTTPException(status_code=400, detail="TTL indexes must be on a single field")

    keys = [(f.field, f.direction) for f in body.fields]
    kwargs: dict = {"unique": body.unique, "sparse": body.sparse}

    if body.name:
        kwargs["name"] = body.name
    if body.ttl is not None:
        kwargs["expireAfterSeconds"] = body.ttl
    if body.partial_filter_expression:
        kwargs["partialFilterExpression"] = body.partial_filter_expression

    try:
        index_name = database.db[collection_name].create_index(keys, **kwargs)
    except OperationFailure as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"created": index_name}


@router.delete("/{index_name}")
def delete_index(collection_name: str, index_name: str):
    if collection_name not in database.db.list_collection_names():
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    try:
        database.db[collection_name].drop_index(index_name)
    except OperationFailure as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"deleted": index_name}
