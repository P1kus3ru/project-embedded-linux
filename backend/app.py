# backend/app.py
from fastapi import FastAPI
from routes.advance_turn import router as advance_router
from routes.fetch_encounter import router as encounter_router

app = FastAPI()

app.include_router(advance_router)
app.include_router(encounter_router)