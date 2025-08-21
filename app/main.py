import math
from sqlalchemy import func
from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from .utils import import_pd_from_csv, import_ziploc_from_csv, generate_star_ratings
from sqlalchemy.future import select
from .database import get_db, engine, async_session
from .models import Base, User, ProviderData, ZipLoc, StarRating

from .prompts import DB_EXPLAIN, PREAMBLE

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
    await generate_star_ratings()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/ask/")
async def ai(query: str):

    prompt = PREAMBLE + query + "\n\n" + DB_EXPLAIN

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"response": response.choices[0].message.content}

@app.get("/providers/")
async def get_providers(zipcode: str = Query(..., min_length=5, max_length=10), drg: str = Query(...), radius: int = Query(25, ge=1, le=200)):
    async with async_session() as session:  
        stmt = select(ZipLoc).where(ZipLoc.Zip == zipcode)
        result = await session.execute(stmt)
        zip_row = result.scalar_one_or_none()
        if zip_row is None:
            return ["Invalid Zip"]  # ZIP does not exist
        target_lat = zip_row.Lat 
        target_lon = zip_row.Lon

        distance_expr = (
            6371 * 2 * func.asin(
                func.sqrt(
                    func.pow(func.sin(func.radians(target_lat - ProviderData.zip_lat)/2), 2) +
                    func.cos(func.radians(ProviderData.zip_lat)) *
                    func.cos(func.radians(target_lat)) *
                    func.pow(func.sin(func.radians(target_lon - ProviderData.zip_lon)/2), 2)
                )
            )
        )
        stmt = select(ProviderData).where(distance_expr <= radius, ProviderData.DRG_Desc.ilike(f"%{drg}%")).order_by(ProviderData.Avg_Mdcr_Pymt_Amt.desc()).limit(20)
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