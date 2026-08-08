import os
import time
from src.utils.logger import get_logger

logger = get_logger("DatasetService")

class DatasetService:
    def __init__(self):
        pass

    def prepare_dataset(self, audio_path: str, whisper_size: str = "base", language: str = "th"):
        try:
            logger.info(f"Starting dataset preparation for: {audio_path} with Whisper-{whisper_size}")
            import os
            import time
            import torch
            import torchaudio
            from transformers import pipeline
            from pythainlp.tokenize import word_tokenize
            import soundfile as sf
            
            workspace_dir = os.environ.get("APP_WORKSPACE_DIR", "./data")
            dataset_dir = f"{workspace_dir}/dataset"
            os.makedirs(dataset_dir, exist_ok=True)
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # 1. VAD Chunking (using silero-vad)
            logger.info("Loading Silero VAD...")
            model_vad, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False, onnx=False)
            (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils
            
            wav = read_audio(audio_path, sampling_rate=16000)
            # You can tweak VAD parameters here (e.g., threshold, min_speech_duration_ms)
            speech_timestamps = get_speech_timestamps(wav, model_vad, sampling_rate=16000, threshold=0.5, min_speech_duration_ms=250)
            
            # 2. Setup Whisper for Transcription
            logger.info(f"Loading Whisper Model (openai/whisper-{whisper_size})...")
            # Using generate_kwargs to force language if specified
            generate_kwargs = {}
            if language != "auto":
                generate_kwargs["language"] = language
                
            transcriber = pipeline(
                "automatic-speech-recognition", 
                model=f"openai/whisper-{whisper_size}", 
                device=0 if device=="cuda" else -1,
                generate_kwargs=generate_kwargs
            )
            
            metadata_path = f"{dataset_dir}/metadata.csv"
            
            total_chunks = 0
            with open(metadata_path, "a", encoding="utf-8") as f:
                for i, segment in enumerate(speech_timestamps):
                    # Extract chunk
                    start_sample = segment['start']
                    end_sample = segment['end']
                    chunk_audio = wav[start_sample:end_sample]
                    
                    # Save chunk to disk
                    chunk_name = f"chunk_{int(time.time())}_{i}.wav"
                    chunk_path = f"{dataset_dir}/{chunk_name}"
                    torchaudio.save(chunk_path, chunk_audio.unsqueeze(0), 16000)
                    
                    # 3. Transcribe Chunk
                    result = transcriber(chunk_path)
                    raw_text = result.get("text", "").strip()
                    
                    # 4. Thai NLP Normalization (Remove whitespaces for TTS)
                    if language == "th" or any("\u0E00" <= c <= "\u0E7F" for c in raw_text):
                        normalized_text = "".join(word_tokenize(raw_text, keep_whitespace=False))
                    else:
                        normalized_text = raw_text
                        
                    # Write to metadata
                    if normalized_text:
                        f.write(f"{chunk_name}|{normalized_text}\n")
                        total_chunks += 1
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            logger.info(f"Dataset generated successfully. {total_chunks} chunks written.")
            return True, f"✅ หั่นไฟล์และถอดข้อความสำเร็จ (Whisper-{whisper_size})! ได้ {total_chunks} ท่อนเสียง"
        except Exception as e:
            logger.error(f"Dataset preparation failed: {str(e)}", exc_info=True)
            return False, f"❌ Error generating dataset: {str(e)}"

dataset_service = DatasetService()
