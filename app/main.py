from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import ValidationError
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from .db import users, init_indexes, doc_to_user_out, oid
from .models import UserIn, UserUpdate, UserOut

app = FastAPI(
    title="Users API (FastAPI + MongoDB/Motor)",
    version="1.0.0",
)

@app.on_event("startup")
async def on_startup():
    await init_indexes()

# create
@app.post("/users", response_model=UserOut, status_code=201)
async def create_user(payload: UserIn):
    try:
        doc = payload.model_dump()
        result = await users.insert_one(doc)
        created = await users.find_one({"_id": result.inserted_id})
        return doc_to_user_out(created)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

# READ list (busca/filtros/paginação)
@app.get("/users", response_model=List[UserOut])
async def list_users(
    response: Response,
    q: Optional[str] = Query(None, description="Busca por nome (regex case-insensitive)"),
    min_age: Optional[int] = Query(None, ge=0),
    max_age: Optional[int] = Query(None, ge=0),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    filt: Dict[str, Any] = {}

    if q:
        filt["name"] = {"$regex": q, "$options": "i"}

    if min_age is not None or max_age is not None:
        age_f: Dict[str, Any] = {}
        if min_age is not None:
            age_f["$gte"] = min_age
        if max_age is not None:
            age_f["$lte"] = max_age
        if age_f:
            filt["age"] = age_f

    if is_active is not None:
        filt["is_active"] = is_active

    skip = (page - 1) * limit
    cursor = users.find(filt).sort("name", 1).skip(skip).limit(limit)
    items = [doc_to_user_out(doc) async for doc in cursor]
    total = await users.count_documents(filt)
    response.headers["X-Total-Count"] = str(total)
    return items

def _validate_object_id_or_400(id: str) -> ObjectId:
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido.")
    return oid(id)

# read
@app.get("/users/{id}", response_model=UserOut)
async def get_user(id: str):
    _id = _validate_object_id_or_400(id)
    doc = await users.find_one({"_id": _id})
    if not doc:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return doc_to_user_out(doc)

# update
@app.put("/users/{id}", response_model=UserOut)
async def update_user(id: str, payload: UserUpdate):
    _id = _validate_object_id_or_400(id)
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not update:
        doc = await users.find_one({"_id": _id})
        if not doc:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        return doc_to_user_out(doc)

    try:
        res = await users.update_one({"_id": _id}, {"$set": update})
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")

    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    doc = await users.find_one({"_id": _id})
    return doc_to_user_out(doc)

# delete
@app.delete("/users/{id}", status_code=204)
async def delete_user(id: str):
    _id = _validate_object_id_or_400(id)
    res = await users.delete_one({"_id": _id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return Response(status_code=204)
