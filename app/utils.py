import csv
import random
from sqlalchemy.future import select
from .models import ProviderData, ZipLoc, StarRating
from .database import async_session

async def import_pd_from_csv(file_path: str):
    async with async_session() as session:
        async with session.begin():
            with open(file_path, newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    pd = ProviderData(
                        Prvdr_CCN=row["Prvdr_CCN"],
                        Prvdr_Org_Name=row["Prvdr_Org_Name"],
                        Prvdr_City=row["Prvdr_City"],
                        Prvdr_St=row["Prvdr_St"],
                        Prvdr_State_FIPS=row["Prvdr_State_FIPS"],
                        Prvdr_Zip5=row["Prvdr_Zip5"],
                        Prvdr_State_Abrvtn=row["Prvdr_State_Abrvtn"],
                        Prvdr_RUCA=row["Prvdr_RUCA"],
                        Prvdr_RUCA_Desc=row["Prvdr_RUCA_Desc"],
                        DRG_Cd=row["DRG_Cd"],
                        DRG_Desc=row["DRG_Desc"],
                        Tot_Dschrgs=int(row["Tot_Dschrgs"]) if row["Tot_Dschrgs"] else None,
                        Avg_Submtd_Cvrd_Chrg=float(row["Avg_Submtd_Cvrd_Chrg"]) if row["Avg_Submtd_Cvrd_Chrg"] else None,
                        Avg_Tot_Pymt_Amt=float(row["Avg_Tot_Pymt_Amt"]) if row["Avg_Tot_Pymt_Amt"] else None,
                        Avg_Mdcr_Pymt_Amt=float(row["Avg_Mdcr_Pymt_Amt"]) if row["Avg_Mdcr_Pymt_Amt"] else None,
                        zip_lat=float(row["zip_lat"]) if row["zip_lat"] else None,
                        zip_lon=float(row["zip_lon"]) if row["zip_lon"] else None,
                    )
                    session.add(pd)
        await session.commit()

async def import_ziploc_from_csv(file_path: str):
    async with async_session() as session:
        async with session.begin():
            with open(file_path, newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    zl = ZipLoc(Zip=row['Zip'], Lat=float(row['Lat']), Lon=float(row['Lon']))
                    session.add(zl)
        await session.commit()


async def generate_star_ratings():
    async with async_session() as session:
        async with session.begin():
                    # Get all unique Prvdr_CCNs
            stmt = select(ProviderData.Prvdr_CCN).distinct()
            result = await session.execute(stmt)
            unique_ccns = [row[0] for row in result.all()]

            # For each CCN, create a new entry with random_score
            for ccn in unique_ccns:
                # Option 1: create new row with random_score only
                sr = StarRating(
                    Prvdr_CCN=ccn,
                    Rating=random.randint(1, 10)
                )
                session.add(sr)
        await session.commit()