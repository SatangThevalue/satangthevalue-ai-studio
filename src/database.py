from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

# Use custom workspace if running on Colab, otherwise use local ./data
workspace_dir = os.environ.get("APP_WORKSPACE_DIR", "./data")
DATABASE_URL = f"sqlite:///{workspace_dir}/app.db"

# Ensure data directory exists
os.makedirs(workspace_dir, exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class VoiceProfile(Base):
    __tablename__ = "voice_profiles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    reference_audio_path = Column(String)
    is_custom_lora = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class GenerationTask(Base):
    __tablename__ = "generation_tasks"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    voice_profile_id = Column(Integer)
    status = Column(String, default="pending") # pending, processing, completed, failed
    output_path = Column(String, nullable=True)
    generation_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
