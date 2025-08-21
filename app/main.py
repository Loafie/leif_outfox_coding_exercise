from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db, engine
from .models import Base, User

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

app = FastAPI(title="FastAPI + Async SQLAlchemy + PostgreSQL + OpenAI")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/ai")
async def ai(prompt: str):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50
    )
    return {"response": response.choices[0].message.content}