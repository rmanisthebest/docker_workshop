from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
import logging
from .schema import DeviceInfo, Configuration
from . import crud, models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.post('/device/info')
def save_device_info(info: DeviceInfo, db=Depends(db)):
    object_in_db = crud.get_device_info(db, info.token)
    if object_in_db:
        raise HTTPException(400, detail= crud.error_message('This device info already exists'))
    return crud.save_device_info(db,info)

@app.get('/device/info/{token}')
def get_device_info(token: str, db=Depends(db)):
    info = crud.get_device_info(db,token)
    if info:
        logging.info(info)
        return info
    else:
        raise HTTPException(404, crud.error_message('No device found for token {}'.format(token)))

@app.get('/device/info')
def get_all_device_info(db=Depends(db)):
    return crud.get_device_info(db)

@app.post('/configuration')
def save_configuration(config: Configuration, db=Depends(db)):
    # always maintain one config
    crud.delete_nudges_configuration(db)
    return crud.save_nudges_configuration(db, config)

@app.get('/configuration')
def get_configuration(db=Depends(db)):
    config = crud.get_nudges_configuration(db)
    if config:
        return config
    else:
        raise HTTPException(404, crud.error_message('No configuration set'))