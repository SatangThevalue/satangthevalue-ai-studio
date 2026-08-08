import os
import soundfile as sf
import pyloudnorm as pyln
import librosa
from pedalboard import Pedalboard, Compressor, HighpassFilter, LowShelfFilter, HighShelfFilter
from src.utils.logger import get_logger

logger = get_logger("AudioService")

class AudioEnhancer:
    def __init__(self):
        pass

    def process_audio(self, input_path: str, output_path: str):
        try:
            logger.info(f"Starting dynamic audio enhancement for: {input_path}")
            import time
            import os
            import soundfile as sf
            
            # 1. Ingestion via pydub
            from pydub import AudioSegment
            logger.info("Loading audio with pydub...")
            audio = AudioSegment.from_file(input_path).set_frame_rate(24000).set_channels(1)
            
            temp_wav = f"/tmp/temp_ingest_{int(time.time())}.wav"
            audio.export(temp_wav, format="wav")
            
            # 2. Studio EQ & Compression via pedalboard
            import librosa
            from pedalboard import Pedalboard, Compressor, HighpassFilter, NoiseGate
            
            logger.info("Applying Pedalboard effects (EQ, NoiseGate, Compressor)...")
            audio_data, sr = librosa.load(temp_wav, sr=24000)
            board = Pedalboard([
                NoiseGate(threshold_db=-35.0, ratio=1.5, release_ms=250),
                HighpassFilter(cutoff_frequency_hz=80), 
                Compressor(threshold_db=-18, ratio=3.0)
            ])
            processed_audio = board(audio_data, sr)
            
            # 3. LUFS Normalization via pyloudnorm
            import pyloudnorm as pyln
            logger.info("Normalizing to -16 LUFS...")
            meter = pyln.Meter(sr)
            loudness = meter.integrated_loudness(processed_audio)
            final_audio = pyln.normalize.loudness(processed_audio, loudness, -16.0)
            
            # 4. Export
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            sf.write(output_path, final_audio, sr)
            
            # Cleanup temp
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            
            logger.info(f"Audio enhanced successfully: {output_path}")
            return True, f"✅ ล้างเสียง (EQ, Gate) และปรับ -16 LUFS สำเร็จ! บันทึกที่ {output_path}"
        except Exception as e:
            logger.error(f"Audio enhancement failed: {str(e)}", exc_info=True)
            return False, f"❌ Error processing audio: {str(e)}"

audio_enhancer = AudioEnhancer()
