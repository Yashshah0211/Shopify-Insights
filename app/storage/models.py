from sqlalchemy import Column, Integer, String, Text
from app.storage.db import Base

class Brand(Base):
    __tablename__ = 'brands'
    id = Column(Integer, primary_key=True, index=True)
    website = Column(String(255), unique=True, nullable=False, index=True)
    json = Column(Text)
