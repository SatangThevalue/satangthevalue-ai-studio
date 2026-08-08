# Mobile Audio Processing Workflow

This document explains the End-to-End (E2E) workflow that occurs when a user uploads a raw audio file recorded from a mobile phone into the **SatangTheValue AI Studio** pipeline.

## 📱 The Challenge with Mobile Audio
Audio recorded on mobile phones typically suffers from several issues that ruin AI TTS training:
1. **Background Noise**: Hissing, fans, or street noise.
2. **Room Reverberation**: Echo caused by recording in untreated rooms.
3. **Uneven Dynamics**: The volume jumps up and down depending on how close the speaker is to the phone.
4. **Long Uncut Files**: Mobile recordings are often 10-30 minutes long, which will cause Out-Of-Memory (OOM) errors during AI training.

## ⚙️ The E2E Processing Pipeline

When the user uploads the file in **Tab 2 (Data Collection & Prep)** and clicks **Process & Save**, the system automatically executes the following pipeline:

### Step 1: Ingestion & Format Conversion
- Gradio receives the file (usually `.m4a` or `.mp3` from phones).
- The system reads the audio into a mathematical array (NumPy) and converts it to a Mono channel to ensure consistency for TTS processing.

### Step 2: Studio-Grade Enhancement (`src/services/audio_service.py`)
The system applies DSP (Digital Signal Processing) using Spotify's `pedalboard` library:
- **Highpass Filter (80Hz)**: Cuts out low-end rumble (like AC noise or wind hitting the phone mic).
- **Podcast EQ**: Boosts lows (150Hz) for warmth and highs (5000Hz) for clarity.
- **Dynamic Range Compressor**: Tames loud peaks and boosts quiet whispers so the volume is perfectly even.
- **LUFS Normalization (-14 LUFS)**: Uses `pyloudnorm` to adjust the overall loudness to standard broadcast levels.

### Step 3: Dataset Preparation (`src/services/dataset_service.py`)
- **VAD Slicing**: The 30-minute enhanced audio is automatically sliced into tiny chunks (3 to 10 seconds long), discarding long periods of silence.
- **Auto-Transcription (WhisperX)**: An AI listens to each tiny chunk and writes down exactly what was said.
- **Metadata Generation**: The system creates a `metadata.csv` file mapping each audio chunk to its text (e.g., `chunk_001.wav|สวัสดีครับ`).

### Step 4: Persistent Storage
- Instead of keeping these files in Colab's temporary memory, the system routes all outputs (Enhanced Audio, Chunks, and `metadata.csv`) directly into your **Google Drive Workspace** (`APP_WORKSPACE_DIR`).
- Result: The user can now safely navigate to **Tab 3** and click "Start Fine-Tuning" because the dataset is perfectly cleaned, sliced, and formatted.
