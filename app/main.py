from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from .utils import import_pd_from_csv, import_ziploc_from_csv
from sqlalchemy.future import select
from .database import get_db, engine, async_session
from .models import Base, User, ProviderData

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
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "NY_sample_data.csv")
    await import_pd_from_csv(csv_path)
    csv_path2 = os.path.join(os.path.dirname(__file__), "..", "data", "zips_to_latlon.csv")
    await import_ziploc_from_csv(csv_path2)

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

@app.get("/providers/")
async def get_providers(zipcode: str = Query(..., min_length=5, max_length=10)):
    """
    Return up to 10 providers matching the given zipcode.
    """
    async with async_session() as session:  # async SQLAlchemy session
        # Build query
        stmt = select(ProviderData).where(ProviderData.Prvdr_Zip5 == zipcode).limit(10)
        result = await session.execute(stmt)
        providers = result.scalars().all()  # List[ProviderData]

        # Convert to list of dicts
        return [  # JSON-serializable
            {
                "Prvdr_CCN": p.Prvdr_CCN,
                "Prvdr_Org_Name": p.Prvdr_Org_Name,
                "Prvdr_City": p.Prvdr_City,
                "Prvdr_St": p.Prvdr_St,
                "Prvdr_State_FIPS": p.Prvdr_State_FIPS,
                "Prvdr_Zip5": p.Prvdr_Zip5,
                "Prvdr_State_Abrvtn": p.Prvdr_State_Abrvtn,
                "Prvdr_RUCA": p.Prvdr_RUCA,
                "Prvdr_RUCA_Desc": p.Prvdr_RUCA_Desc,
                "DRG_Cd": p.DRG_Cd,
                "DRG_Desc": p.DRG_Desc,
                "Tot_Dschrgs": p.Tot_Dschrgs,
                "Avg_Submtd_Cvrd_Chrg": p.Avg_Submtd_Cvrd_Chrg,
                "Avg_Tot_Pymt_Amt": p.Avg_Tot_Pymt_Amt,
                "Avg_Mdcr_Pymt_Amt": p.Avg_Mdcr_Pymt_Amt,
                "zip_lat": p.zip_lat,
                "zip_lon": p.zip_lon,
            }
            for p in providers
        ]