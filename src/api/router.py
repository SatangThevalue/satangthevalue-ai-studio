from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.database import get_db, GenerationTask
from src.services.tts_service import tts_service
from pydantic import BaseModel
import time

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    speed: float = 1.0
    reference_audio_id: int = None

def process_tts_task(task_id: int, request: TTSRequest, db: Session):
    task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
    if not task:
        return
        
    task.status = "processing"
    db.commit()
    
    start_time = time.time()
    try:
        # Call the TTS service
        output_path = tts_service.generate_tts(text=request.text, speed=request.speed)
        
        task.output_path = output_path
        task.status = "completed"
    except Exception as e:
        task.status = f"failed: {str(e)}"
        
    task.generation_time_ms = (time.time() - start_time) * 1000
    db.commit()

@router.post("/generate")
def generate_tts(request: TTSRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 1. Create task in DB
    new_task = GenerationTask(text=request.text, status="pending")
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # 2. Add to background queue
    background_tasks.add_task(process_tts_task, new_task.id, request, db)
    
    # 3. Return Job ID immediately
    return {"status": "accepted", "job_id": new_task.id, "message": "TTS generation started in background."}

@router.get("/jobs/{job_id}")
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    task = db.query(GenerationTask).filter(GenerationTask.id == job_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": task.id,
        "status": task.status,
        "output_path": task.output_path,
        "generation_time_ms": task.generation_time_ms
    }
