import os
import time

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
        
        print(f"Mock: Slicing and transcribing {audio_path} via WhisperX...")
        time.sleep(3) # Simulate heavy WhisperX processing
        
        # Use timestamp to ensure chunk names are unique across different uploads
        uid = int(time.time())
        
        # Use "a" (append) mode instead of "w" (write/overwrite)
        with open(metadata_path, "a", encoding="utf-8") as f:
            f.write(f"chunk_{uid}_1.wav|สวัสดีครับ ยินดีต้อนรับเข้าสู่รายการ\n")
            f.write(f"chunk_{uid}_2.wav|วันนี้เราจะมาพูดถึงเรื่องเทคโนโลยีเอไอ\n")
            
        return True, f"Dataset prepared and APPENDED successfully! Metadata updated at {metadata_path}"

dataset_service = DatasetService()
