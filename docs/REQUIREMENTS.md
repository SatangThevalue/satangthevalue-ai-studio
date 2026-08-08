# Project Requirements

## 1. Business Requirements
- **Commercial Use**: The solution must use models and tools that permit commercial usage (e.g., MIT, Apache 2.0). F5-TTS has been selected to meet this.
- **Zero-Shot & Fine-Tuning**: Must support cloning voices on-the-fly (Zero-shot) and deeper adaptation via LoRA (Fine-Tuning).
- **Extensibility**: Must be ready to integrate with external systems (e.g., a Next.js frontend or automation workflows).

## 2. Technical Requirements
- **Python `uv`**: Must use `uv` for lightning-fast dependency management, crucial for minimizing Colab startup times.
- **FastAPI + Gradio**: The UI must be built with Gradio and mounted onto a FastAPI application.
- **Data Persistence**: 
  - Audio files: Saved to disk (Local or Google Drive when on Colab).
  - Metadata & Logs: Saved to a local `SQLite` database.
- **UI Data Collection**: The Gradio UI must support direct microphone recording and file uploads.
- **Text Prompter**: The UI should include a random text prompter (Thai sentences) to guide users when recording their voice.

## 3. Implementation Phases
- **Phase 1**: Environment setup (`pyproject.toml`, FastAPI + Gradio skeleton), SQLite integration.
- **Phase 2**: Audio enhancement pipeline (Denoise, Normalize) & Auto-Transcription integration (WhisperX).
- **Phase 3**: F5-TTS integration (Zero-shot inference API and UI).
- **Phase 4**: LoRA Fine-tuning pipeline & ONNX Export.
