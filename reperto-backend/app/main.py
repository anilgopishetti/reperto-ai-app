# backend/app/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

from .database import database
from .schemas import UserCreate, UserLogin, Token
from .auth import create_user, authenticate_user
from .ai import parse_text_endpoint

app = FastAPI(title="Reperto AI Backend")

# CORS Configuration - Allow requests from frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://localhost:19006",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:19006",
        "http://10.0.2.2:8081",  # Android emulator
        "*",  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/auth/signup", response_model=dict)
async def signup(payload: UserCreate):
    success = await create_user(payload.name, payload.email, payload.password)
    if not success:
        raise HTTPException(status_code=400, detail="User already exists")
    return {"status":"ok"}

@app.post("/auth/login", response_model=Token)
async def login(payload: UserLogin):
    token = await authenticate_user(payload.email, payload.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token}

@app.post("/ai/parse-text")
async def parse_text(body: dict):
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")

    return parse_text_endpoint(text)

