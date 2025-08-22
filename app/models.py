from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class ZipLoc(Base):
    __tablename__ = "zip_locations"
    zip = Column(String, primary_key=True, index=True)
    lat = Column(Float)
    lon = Column(Float)

class StarRating(Base):
    __tablename__ = "star_ratings"
    prvdr_ccn = Column(String, primary_key = True, index=True)
    rating = Column(Integer)
    

class ProviderData(Base):
    __tablename__ = "provider_data"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # optional surrogate key
    prvdr_ccn = Column(String, index=True)
    prvdr_org_name = Column(String)
    prvdr_city = Column(String)
    prvdr_st = Column(String)
    prvdr_state_fips = Column(String)
    prvdr_zip5 = Column(String)
    prvdr_state_abrvtn = Column(String)
    prvdr_ruca = Column(String)
    prvdr_ruca_desc = Column(String)
    drg_cd = Column(String)
    drg_desc = Column(String)
    tot_dschrgs = Column(Integer)
    avg_submtd_cvrd_chrg = Column(Float)
    avg_tot_pymt_amt = Column(Float)
    avg_mdcr_pymt_amt = Column(Float)
    zip_lat = Column(Float)
    zip_lon = Column(Float)