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
                        prvdr_ccn=row["Prvdr_CCN"],
                        prvdr_org_name=row["Prvdr_Org_Name"],
                        prvdr_city=row["Prvdr_City"],
                        prvdr_st=row["Prvdr_St"],
                        prvdr_state_fips=row["Prvdr_State_FIPS"],
                        prvdr_zip5=row["Prvdr_Zip5"],
                        prvdr_state_abrvtn=row["Prvdr_State_Abrvtn"],
                        prvdr_ruca=row["Prvdr_RUCA"],
                        prvdr_ruca_desc=row["Prvdr_RUCA_Desc"],
                        drg_cd=row["DRG_Cd"],
                        drg_desc=row["DRG_Desc"],
                        tot_dschrgs=int(row["Tot_Dschrgs"]) if row["Tot_Dschrgs"] else None,
                        avg_submtd_cvrd_chrg=float(row["Avg_Submtd_Cvrd_Chrg"]) if row["Avg_Submtd_Cvrd_Chrg"] else None,
                        avg_tot_pymt_amt=float(row["Avg_Tot_Pymt_Amt"]) if row["Avg_Tot_Pymt_Amt"] else None,
                        avg_mdcr_pymt_amt=float(row["Avg_Mdcr_Pymt_Amt"]) if row["Avg_Mdcr_Pymt_Amt"] else None,
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
                    zl = ZipLoc(zip=row['Zip'], lat=float(row['Lat']), lon=float(row['Lon']))
                    session.add(zl)
        await session.commit()


async def generate_star_ratings():
    async with async_session() as session:
        async with session.begin():
                    # Get all unique Prvdr_CCNs
            stmt = select(ProviderData.prvdr_ccn).distinct()
            result = await session.execute(stmt)
            unique_ccns = [row[0] for row in result.all()]

            # For each CCN, create a new entry with random_score
            for ccn in unique_ccns:
                # Option 1: create new row with random_score only
                sr = StarRating(
                    prvdr_ccn=ccn,
                    rating=random.randint(1, 10)
                )
                session.add(sr)
        await session.commit()