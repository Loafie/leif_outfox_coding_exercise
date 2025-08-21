from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class ProviderData(Base):
    __tablename__ = "provider_data"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # optional surrogate key
    Prvdr_CCN = Column(String, index=True)
    Prvdr_Org_Name = Column(String)
    Prvdr_City = Column(String)
    Prvdr_St = Column(String)
    Prvdr_State_FIPS = Column(String)
    Prvdr_Zip5 = Column(String)
    Prvdr_State_Abrvtn = Column(String)
    Prvdr_RUCA = Column(String)
    Prvdr_RUCA_Desc = Column(String)
    DRG_Cd = Column(String)
    DRG_Desc = Column(String)
    Tot_Dschrgs = Column(Integer)
    Avg_Submtd_Cvrd_Chrg = Column(Float)
    Avg_Tot_Pymt_Amt = Column(Float)
    Avg_Mdcr_Pymt_Amt = Column(Float)
    zip_lat = Column(Float)
    zip_lon = Column(Float)