import math
from sqlalchemy import func, text
from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from .utils import import_pd_from_csv, import_ziploc_from_csv, generate_star_ratings
from sqlalchemy.future import select
from .database import get_db, engine, async_session
from .models import Base, User, ProviderData, ZipLoc, StarRating
from fastapi.responses import JSONResponse
import json

from .prompts import DB_EXPLAIN, PREAMBLE, META_AFTER, HAVERSINE_SQL

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
    async with async_session() as session:
        await session.execute(text(HAVERSINE_SQL))
        await session.commit()

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
    resp = response.choices[0].message.content.replace("```sql\n","").replace("\n```","")
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(text(resp))
            rows = [dict(row) for row in result.mappings().all()]
            # Force rollback so no writes persist to prevent particularly harmful prompt injection
            await session.rollback()
            db_resp = JSONResponse(content=rows)

    second_prompt = META_AFTER + "\nINITIAL QUESTION:\n" + query + "\n\nTHE QUERY:\n" + resp + "\n\nDATABASE RESPONSE:\n" + db_resp.body.decode("utf-8") + "\n\nFIRST PROMPT:\n" + prompt
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": second_prompt}]
    )
    return [{"Response" : response.choices[0].message.content}]

@app.get("/providers/")
async def get_providers(zipcode: str = Query(..., min_length=5, max_length=10), drg: str = Query(...), radius: int = Query(25, ge=1, le=200)):
    async with async_session() as session:  
        stmt = select(ZipLoc).where(ZipLoc.zip == zipcode)
        result = await session.execute(stmt)
        zip_row = result.scalar_one_or_none()
        if zip_row is None:
            return ["Invalid Zip"]  # ZIP does not exist
        target_lat = zip_row.lat 
        target_lon = zip_row.lon

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
        stmt = select(ProviderData).where(distance_expr <= radius, ProviderData.drg_desc.ilike(f"%{drg}%")).order_by(ProviderData.avg_mdcr_pymt_amt.desc()).limit(20)
        result = await session.execute(stmt)
        providers = result.scalars().all()  # List[ProviderData]

        # Convert to list of dicts
        return [  # JSON-serializable
            {
                "prvdr_ccn": p.prvdr_ccn,
                "prvdr_org_name": p.prvdr_org_name,
                "prvdr_city": p.prvdr_city,
                "prvdr_st": p.prvdr_st,
                "prvdr_state_fips": p.prvdr_state_fips,
                "prvdr_zip5": p.prvdr_zip5,
                "prvdr_state_abrvtn": p.prvdr_state_abrvtn,
                "prvdr_ruca": p.prvdr_ruca,
                "prvdr_ruca_desc": p.prvdr_ruca_desc,
                "drg_cd": p.drg_cd,
                "drg_desc": p.drg_desc,
                "tot_dschrgs": p.tot_dschrgs,
                "avg_submtd_cvrd_chrg": p.avg_submtd_cvrd_chrg,
                "avg_tot_pymt_amt": p.avg_tot_pymt_amt,
                "avg_mdcr_pymt_amt": p.avg_mdcr_pymt_amt,
                "zip_lat": p.zip_lat,
                "zip_lon": p.zip_lon,
            }
            for p in providers
        ]