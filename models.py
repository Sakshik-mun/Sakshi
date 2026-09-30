from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class FinancialProfile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    monthly_income = Column(Float)
    monthly_expenses = Column(Float)
    total_emi = Column(Float)
    credit_limit = Column(Float)
    credit_used = Column(Float)
    credit_score = Column(Integer)
    dti = Column(Float)
    utilization = Column(Float)
    last_advice = Column(Text, nullable=True)  # cached JSON
    updated_at = Column(DateTime, default=datetime.utcnow)

class ScoreHistory(Base):
    __tablename__ = "score_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    score = Column(Integer)
    dti = Column(Float)
    utilization = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
