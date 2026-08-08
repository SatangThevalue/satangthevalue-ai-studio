# src/config.py
# Centralized configuration for Models and Languages

SUPPORTED_LANGUAGES = {
    "Auto-Detect": "auto",
    "Thai (ภาษาไทย)": "th",
    "English (ภาษาอังกฤษ)": "en",
    "Chinese (ภาษาจีน)": "zh",
    "Japanese (ภาษาญี่ปุ่น)": "ja",
    "Korean (ภาษาเกาหลี)": "ko"
}

# Model Registry
# This allows easy addition of new HuggingFace models without touching UI code.
SUPPORTED_MODELS = {
    "TTS": {
        "F5-TTS Base": {
            "hf_repo": "SWivid/F5-TTS",
            "cli_command": "f5-tts_infer-cli",
            "supports_language_flag": False # F5-TTS detects automatically or doesn't use a flag
        },
        "CosyVoice-Base": {
            "hf_repo": "FunAudioLLM/CosyVoice-300M",
            "cli_command": "cosyvoice-cli",
            "supports_language_flag": False 
        },
        "XTTS-v2": {
            "hf_repo": "coqui/XTTS-v2",
            "cli_command": "xtts-cli", # Hypothetical CLI for XTTS
            "supports_language_flag": True
        }
    },
    "Transcription": {
        "WhisperX (Large v3)": {
            "hf_repo": "Systran/faster-whisper-large-v3"
        },
        "Whisper (Medium)": {
            "hf_repo": "openai/whisper-medium"
        }
    }
}

def get_tts_model_names():
    return list(SUPPORTED_MODELS["TTS"].keys())

def get_transcription_model_names():
    return list(SUPPORTED_MODELS["Transcription"].keys())

def get_all_downloadable_models():
    models = {}
    for category in SUPPORTED_MODELS.values():
        for name, data in category.items():
            models[name] = data["hf_repo"]
    return models
