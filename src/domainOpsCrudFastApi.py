from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import List, Dict, Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json

from .domainOpsCrud import DomainOpsLoggerCRUD
class Category(BaseModel):
    name: str
    loc: List[str | int | float | bool | None]
class KeyValueDelete(Category):
    key: str
class KeyValue(KeyValueDelete):
    value: Dict | str | int | float | bool | None | List[Dict | str | int | float | bool | None]
class Location(BaseModel):
    loc: List[str | int | float | bool | None]
class CategoryValue(Category):
    value: Dict | str | int | float | bool | None | List[Dict | str | int | float | bool | None]
class LoggerCreate(Category):
    domains: List[str] | None = None
    operation: str | None = None
class LoggerUpdate(Category):
    domains: List[str] | None = None
    operation: str | None = None
    new_name: str | None = None

CatNotFound = lambda x: HTTPException(status_code=404, detail= x +" not found")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
dol = DomainOpsLoggerCRUD()


def get_handler(key):
    return getattr(dol.process, key)


@app.post("/logger/create/", response_model=dict)
async def create_logger(infos: LoggerCreate):
    ss = dol.process.logger
    if ss.handlers.nameExists(infos.name, infos.loc):
        raise HTTPException(status_code=400, detail="name already exists")
    if infos.domains is None or infos.operation is None:
        raise HTTPException(status_code=400, detail="domains and operation are required")
    for d in infos.domains:
        if not dol.process.domains.handlers.exists(d, infos.loc):
            raise HTTPException(status_code=400, detail=d+" domain not found")
    if not dol.process.operations.handlers.exists(infos.operation, infos.loc):
        raise HTTPException(status_code=400, detail="operation not found")
    try:
        idd = ss.handlers.create(infos.name, infos.loc, infos.domains, infos.operation)
        return {"logger": infos.name, "status": "created", "id": idd}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/logger/update/", response_model=dict)
async def update_logger(infos: LoggerUpdate):
    ss = dol.process.logger
    if not ss.handlers.exists(infos.name, infos.loc):
        raise CatNotFound("logger")
    try:
        ss.handlers.update(infos.name, infos.loc, infos.new_name, infos.domains, infos.operation)
        return {"logger": infos.name, "status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/{category}/create/", response_model=dict)
async def create_domain(category: str, infos: Category):
    print("category create")
    ss = get_handler(category)
    if ss.handlers.nameExists(infos.name, infos.loc):
        raise HTTPException(status_code=400, detail="name already exists")
    try:
        ss.handlers.create(infos.name, infos.loc)
        return {category: infos.name, "status": "created", "id": idd}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/{category}/read/", response_model= dict)
async def read_domain(category: str, infos: Category):  
    ss = get_handler(category)
    if not ss.handlers.exists(infos.name, infos.loc):
        raise CatNotFound(category)
    return ss.handlers.read(infos.name, infos.loc)
@app.post("/{category}/readAll/", response_model=List[tuple[str, str]])
async def read_all(category: str, loc: Location):
    ss = get_handler(category)
    return ss.handlers.readAll(loc.loc)
@app.post("/{category}/update_name/", response_model=dict)
async def update_domain(category: str, cat: CategoryValue):
    ss = get_handler(category)
    if not ss.handlers.exists(cat.name, cat.loc):
        raise CatNotFound(category)
    ss.handlers.update(cat.value, cat.name, cat.loc)
    return {"status": "name updated"}
@app.post("/{category}/delete/", response_model=dict)
async def delete_domain(category: str, cat: Category):
    ss = get_handler(category)
    if not ss.handlers.exists(cat.name, cat.loc):
        raise CatNotFound(category)

    ss.handlers.delete(cat.name, cat.loc)
    return {"status": "deleted"}
@app.post("/{category}/properties/create/", response_model=dict)
async def create_domain(category: str, infos: KeyValue):
    ss = get_handler(category)
    if not ss.handlers.exists(infos.name, infos.loc):
        raise CatNotFound(category)
    if ss.handlers.existsProperty(infos.name, infos.loc, infos.key):
        raise HTTPException(status_code=400, detail="name already exists")
    try:
        ss.handlers.addNewProperty(infos.name, infos.loc, infos.key, infos.value)
        return {category: f"{infos.key} created for {infos.name}",  "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/{category}/properties/readAll/", response_model= dict)
async def read_domain(category: str, infos: Category):  
    ss = get_handler(category)
    if not ss.handlers.exists(infos.name, infos.loc):
        raise CatNotFound(category)
    return ss.handlers.readProperties(infos.name, infos.loc)
@app.post("/{category}/properties/update/", response_model=dict)
async def update_domain(category: str, cat: KeyValue):
    ss = get_handler(category)
    if not ss.handlers.exists(cat.name, cat.loc):
        raise CatNotFound(category)
    if not ss.handlers.existsProperty(cat.name, cat.loc, cat.key):
        raise CatNotFound("property: " + cat.key)
    ss.handlers.updateProperty(cat.name, cat.loc, cat.key, cat.value)
    return {"status": "name updated"}
@app.post("/{category}/properties/delete/", response_model=dict)
async def delete_domain(category: str, kvd: KeyValueDelete):
    ss = get_handler(category)
    if not ss.handlers.exists(kvd.name, kvd.loc):
        raise CatNotFound(category)
    if not ss.handlers.existsProperty(kvd.name, kvd.loc, kvd.key):
        raise CatNotFound("property: " + kvd.key)
    ss.handlers.deleteProperty(kvd.name, kvd.loc, kvd.key)
    return {"status": "deleted"}