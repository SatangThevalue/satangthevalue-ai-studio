import os
import time
from src.utils.logger import get_logger

logger = get_logger("DatasetService")

class DatasetService:
    def prepare_dataset(self, audio_path: str):
        """
        In a real environment, this would use WhisperX and VAD to:
        1. Silence-split the audio into 3-10s chunks.
        2. Transcribe each chunk.
        3. Write to a metadata.csv file required for TTS training.
        """
        workspace_dir = os.environ.get("APP_WORKSPACE_DIR", "./data")
        dataset_dir = f"{workspace_dir}/dataset"
        os.makedirs(dataset_dir, exist_ok=True)
        
        metadata_path = f"{dataset_dir}/metadata.csv"
        
        logger.info(f"Mocking dataset preparation for: {audio_path}")
        time.sleep(3) # Simulate heavy WhisperX processing
        
        # Use timestamp to ensure chunk names are unique across different uploads
        uid = int(time.time())
        
        # Use "a" (append) mode instead of "w" (write/overwrite)
        try:
            with open(metadata_path, "a", encoding="utf-8") as f:
                f.write(f"chunk_{uid}_1.wav|สวัสดีครับ ยินดีต้อนรับเข้าสู่รายการ\n")
                f.write(f"chunk_{uid}_2.wav|วันนี้เราจะมาพูดถึงเรื่องเทคโนโลยีเอไอ\n")
            logger.info(f"Appended 2 chunks to {metadata_path}")
            return True, f"Dataset prepared and APPENDED successfully! Metadata updated at {metadata_path}"
        except Exception as e:
            logger.error(f"Failed to write metadata: {str(e)}", exc_info=True)
            return False, f"Metadata creation failed: {str(e)}"

dataset_service = DatasetService()
