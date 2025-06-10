from sqlalchemy import Column, Integer, String, Boolean, ARRAY, ForeignKey, DateTime
from sqlalchemy.sql import func
from .database import Base

class Dairy(Base):
    __tablename__ = "dairies"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    milk_movement_names = Column(ARRAY(String), nullable=True)  # Names used in Milk Movement API
    samsara_location_names = Column(ARRAY(String), nullable=True)  # Location names in Samsara
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    dairy_id = Column(String(50), ForeignKey("dairies.id"), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 