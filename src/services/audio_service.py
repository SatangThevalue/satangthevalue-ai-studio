import os
import soundfile as sf
import pyloudnorm as pyln
import librosa
from pedalboard import Pedalboard, Compressor, HighpassFilter, LowShelfFilter, HighShelfFilter
from src.utils.logger import get_logger

logger = get_logger("AudioService")

class AudioEnhancer:
    def __init__(self):
        # Create a Podcast-style processing chain
        self.board = Pedalboard([
            HighpassFilter(cutoff_frequency_hz=80), # Remove low rumble
            LowShelfFilter(cutoff_frequency_hz=150, gain_db=3.0), # Add bass/warmth
            HighShelfFilter(cutoff_frequency_hz=5000, gain_db=2.0), # Add presence/clarity
            Compressor(threshold_db=-15, ratio=3.0, attack_ms=5.0, release_ms=50.0) # Smooth dynamics
        ])
    
    def process_audio(self, input_path: str, output_path: str, target_lufs: float = -14.0):
        try:
            # 1. Load Audio robustly (supports .m4a) and resample to 24000Hz (TTS standard)
            data, rate = librosa.load(input_path, sr=24000, mono=True)
            
            # 2. Apply Pedalboard Effects (EQ + Compressor)
            processed_data = self.board(data, rate)
            
            # 3. LUFS Normalization
            meter = pyln.Meter(rate)
            current_lufs = meter.integrated_loudness(processed_data)
            normalized_data = pyln.normalize.loudness(processed_data, current_lufs, target_lufs)
            
            # 4. Save Audio
            workspace_dir = os.environ.get("APP_WORKSPACE_DIR", "./data")
            final_output_path = f"{workspace_dir}/{output_path}"
            os.makedirs(os.path.dirname(final_output_path), exist_ok=True)
            sf.write(final_output_path, normalized_data, rate)
            logger.info(f"Audio enhanced successfully. Target LUFS: {target_lufs}. Saved to {final_output_path}")
            return True, f"Audio enhanced and normalized successfully. Saved to {final_output_path}"
        except Exception as e:
            logger.error(f"Audio enhancement failed: {str(e)}", exc_info=True)
            return False, f"Audio enhancement failed: {str(e)}"

audio_enhancer = AudioEnhancer()
