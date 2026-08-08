# System Architecture

## 1. High-Level Architecture
The system is built as a single unified application using **FastAPI** as the core backend, with **Gradio** mounted as a sub-application. This allows the system to serve both a graphical user interface and programmatic API endpoints simultaneously.

```
[ Client / Browser ]
        |
        v
[ FastAPI Gateway (Port 8000) ]
        |
        +---> /ui (Gradio Web Interface)
        |       |-- Tab 1: Training & Developer
        |       |-- Tab 2: Generation (Client)
        |       |-- Tab 3: Data Collection & Enhancement
        |
        +---> /api/v1 (RESTful API)
                |-- POST /api/v1/generate
                |-- POST /api/v1/train
                |-- GET  /api/v1/status
```

## 2. Missing Pieces Analyzed & Addressed
During the architectural design, the following crucial components were identified and added to the plan:
1. **Asynchronous Task Queue**: Audio processing and model training are heavily blocking tasks. FastAPI's `BackgroundTasks` or a lightweight queue system (like RQ/Celery) will be required to prevent the UI/API from timing out.
2. **Security & Authentication**: When exposing the FastAPI/Gradio app on a public URL (e.g., via Ngrok on Colab), we must implement Basic Auth or API Key verification.
3. **CORS Middleware**: To support future Next.js frontend integration, FastAPI must have proper CORS configurations.

## 3. Database Schema (SQLite)
SQLite is used to store metadata, track usage, and manage training data.
- **Table: `audio_datasets`**: Stores metadata for raw and processed audio (file path, duration, transcribed text, tags).
- **Table: `training_jobs`**: Tracks LoRA fine-tuning runs (base_model, epochs, loss, status, checkpoint_path).
- **Table: `generation_logs`**: Logs all TTS requests (prompt text, voice profile used, timestamp, generation_time_ms, output_path).

## 4. Environment (Google Colab vs Local)
- **Local/Server**: Runs directly via `uvicorn app.main:app`. SQLite database stored in `./data/app.db`.
- **Google Colab**: The system will mount Google Drive to `/content/drive/MyDrive/Podcast_TTS_Workspace`. The SQLite DB and all heavy assets (checkpoints, ONNX files) will be persisted here to survive instance restarts.
