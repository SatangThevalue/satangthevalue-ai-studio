# UX/UI & API Design Guidelines

Based on modern TTS web application best practices and community implementations of F5-TTS, this document outlines the required features and design patterns for the SatangTheValue AI Studio.

## 1. User Interface (Gradio) Features

### Tab 1: Voice Generation (Client View)
- **Zero-Shot Voice Cloning**: Upload a 5-15s reference audio clip or select from a pre-defined library.
- **Text Input**: Large, accessible text area for long-form scripts.
- **Speech Controls**: 
  - Sliders for Speed (e.g., 0.5x to 2.0x).
  - Emotion/Tone adjustments (if using compatible base model).
- **Batch Processing**: Ability to upload a `.txt` file containing multiple sentences and generate them as separate audio files.
- **Visual Feedback**: 
  - Clear loading states and progress bars during generation.
  - Interactive audio waveform player for immediate playback.
  - Download button for the resulting `.wav` file.

### Tab 2: Training & Developer Configuration
- **Model Selection**: Dropdown to select base models (e.g., F5-TTS base, custom LoRA).
- **Hyperparameter Tuning**: Sliders for Learning Rate, Batch Size, and Epochs.
- **Real-time Logs**: Terminal output view to monitor training progress and loss metrics.
- **Export**: Button to export the fine-tuned model to ONNX format.

### Tab 3: Data Collection & Preparation
- **Microphone Recording**: Direct browser recording capability.
- **Prompt Generator**: A randomized text prompter (Thai sentences) to guide users in recording diverse training data.
- **Audio Enhancement**: Checkboxes to apply `Denoise`, `Dereverb`, and `Podcast EQ`.
- **Metadata Editor**: A data table to review and correct auto-transcribed text (via WhisperX).

## 2. API Design (FastAPI)

The backend must be robust and expose RESTful endpoints for integration with external applications (e.g., Next.js frontend).

- **`POST /api/v1/tts/generate`**
  - Payload: `{"text": "...", "reference_audio_id": "...", "speed": 1.0}`
  - Returns: Audio file URL or binary stream.
- **`POST /api/v1/tts/clone`**
  - Payload: Upload reference audio file.
  - Returns: `voice_profile_id`.
- **`GET /api/v1/jobs/{job_id}`**
  - Returns: Status of a long-running generation or training task (Queued, Processing, Completed).

## 3. Database Schema Updates (SQLite)

To support the above features, the SQLite schema should include:
- **`voice_profiles`**: `id`, `name`, `reference_audio_path`, `is_custom_lora`, `created_at`.
- **`generation_tasks`**: `id`, `text`, `voice_profile_id`, `status`, `output_path`, `generation_time_ms`, `created_at`.
- **`audio_datasets`**: `id`, `raw_audio_path`, `processed_audio_path`, `transcription`, `is_ready_for_training`.

## 4. UX Best Practices
- **Accessibility (WCAG)**: Use high-contrast colors, standard icons (Play, Pause, Stop), and ensure the Gradio UI is keyboard-navigable.
- **Minimize Cognitive Load**: Hide advanced hyperparameter settings behind an "Advanced Settings" accordion.
- **Feedback**: Never leave the user guessing. Always show an active spinner when the FastAPI backend is processing audio.
