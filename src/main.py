from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr

from src.database import init_db
from src.api.router import router as api_router
from src.ui.gradio_app import build_ui

app = FastAPI(title="SatangTheValue AI Studio API", version="1.0.0")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database
@app.on_event("startup")
def on_startup():
    print("Initializing Database...")
    init_db()

# Include REST API
app.include_router(api_router, prefix="/api/v1")

# Mount Gradio UI
gradio_app = build_ui()
app = gr.mount_gradio_app(app, gradio_app, path="/ui")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to SatangTheValue AI Studio TTS Pipeline",
        "docs": "/docs",
        "ui": "/ui"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
