from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
import os

# --- Database Configuration ---
DATABASE_URL = "sqlite:///./mecha_architect.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Red Team Diary Schema (SQLAlchemy Model) ---
class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(String, unique=True, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # The Mission
    target_url = Column(String)
    hydra_persona_id = Column(String)
    
    # The Artifact
    artifact_path = Column(String, comment="Local path to the archived evidence (screenshot, log, etc.)")
    
    # The Analysis
    safety_score_garak = Column(Float, nullable=True)
    safety_score_deepeval = Column(Float, nullable=True)
    quality_metric_score = Column(Float, nullable=True)
    analyst_notes = Column(Text, nullable=True)

def init_db():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
