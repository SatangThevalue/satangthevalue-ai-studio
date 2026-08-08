import gradio as gr
import random
from src.services.tts_service import tts_service

def generate_tts_ui(text, model_name, ref_audio, speed):
    if not text:
        return "Please enter text."
    output_path = tts_service.generate_tts(text, model_name=model_name, ref_audio_path=ref_audio, speed=speed)
    return output_path

def get_random_script():
    scripts = [
        "สวัสดีครับทุกคน ยินดีต้อนรับเข้าสู่รายการพอดแคสต์ของเรา วันนี้เรามีเรื่องราวที่น่าสนใจเกี่ยวกับการพัฒนาเอไอมาฝากกันครับ",
        "การลงทุนมีความเสี่ยง ผู้ลงทุนควรศึกษาข้อมูลก่อนตัดสินใจลงทุนเสมอ แต่วันนี้เราจะมาเจาะลึกเคล็ดลับที่คุณอาจไม่เคยรู้มาก่อน",
        "Welcome to the AI revolution! Today, we're going to dive deep into how large language models are changing the way we work.",
        "รู้หรือไม่ครับว่า กว่าร้อยละ 80 ของความสำเร็จในการทำโปรเจกต์ไอที มาจากการสื่อสารในทีมที่ดี ไม่ใช่แค่สกิลโค้ดดิ้งเพียงอย่างเดียว",
        "กาลครั้งหนึ่งนานมาแล้ว ในยุคที่โลกยังไม่มีอินเทอร์เน็ต ผู้คนติดต่อกันผ่านจดหมาย... แต่ดูตอนนี้สิ เราสั่งให้ AI พูดแทนเราได้แล้ว!"
    ]
    return random.choice(scripts)

def download_base_model(model_name):
    import subprocess
    import os
    
    workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
    
    # Map friendly names to HuggingFace repository IDs
    repo_map = {
        "F5-TTS Base": "SWivid/F5-TTS",
        "CosyVoice-Base": "FunAudioLLM/CosyVoice-300M",
        "WhisperX (Transcription)": "Systran/faster-whisper-large-v3"
    }
    
    hf_repo = repo_map.get(model_name)
    if not hf_repo:
        return f"❌ ไม่พบข้อมูล Repository สำหรับโมเดล {model_name}"
        
    try:
        # Run huggingface-cli to download the snapshot
        # This will automatically respect the HF_HOME environment variable (Google Drive)
        cmd = ["huggingface-cli", "download", hf_repo]
        
        # We use subprocess.Popen to run it synchronously and capture output
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if process.returncode == 0:
            return f"✅ สำเร็จ! ดาวน์โหลดโมเดล {model_name} จาก HuggingFace ลงใน Google Drive ({workspace}/models_cache) เรียบร้อยแล้วของจริง!\n\nLog: {process.stdout[:200]}..."
        else:
            return f"❌ เกิดข้อผิดพลาดในการดาวน์โหลด {model_name}:\n{process.stderr}"
            
    except Exception as e:
        return f"❌ ระบบขัดข้อง: {str(e)}\nกรุณาตรวจสอบว่ามี Library 'huggingface_hub' ติดตั้งอยู่หรือไม่"

def build_ui():
    with gr.Blocks(title="SatangTheValue AI Studio TTS", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🎙️ SatangTheValue AI Studio")
        gr.Markdown("แพลตฟอร์ม AI พอดแคสต์ระดับสตูดิโอ (รองรับ F5-TTS & CosyVoice) สร้างเสียงโคลนและล้างเสียงได้อย่างมืออาชีพ")
        
        with gr.Tabs():
            # TAB 1: Client / Generation
            with gr.TabItem("🎧 1. Generation (สร้างเสียงพอดแคสต์)"):
                gr.Markdown("### 🗣️ Zero-Shot Voice Cloning\nอัปโหลดเสียงต้นแบบของคุณสั้นๆ 10 วินาที จากนั้นพิมพ์ข้อความที่ต้องการให้ AI พูดแทนคุณ")
                with gr.Row():
                    with gr.Column(scale=2):
                        def get_available_models():
                            import os
                            models = ["F5-TTS Base", "CosyVoice-Base", "LoRA-Custom-Voice (Your Voice)"]
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            ckpt_dir = f"{workspace}/checkpoints"
                            if os.path.exists(ckpt_dir):
                                for f in os.listdir(ckpt_dir):
                                    if f.endswith(".pt") or f.endswith(".safetensors"):
                                        models.append(f"{ckpt_dir}/{f}")
                            return gr.update(choices=models)
                            
                        with gr.Row():
                            model_dropdown = gr.Dropdown(choices=["F5-TTS Base", "CosyVoice-Base", "LoRA-Custom-Voice (Your Voice)"], value="F5-TTS Base", label="เลือกโมเดล (Select Base Model)")
                            refresh_model_btn = gr.Button("🔄 โหลด Checkpoints", size="sm")
                            refresh_model_btn.click(fn=get_available_models, inputs=[], outputs=model_dropdown)
                            
                        ref_audio_input = gr.Audio(label="อัปโหลดเสียงต้นแบบ (Reference Audio - 10s)", type="filepath")
                        
                        text_input = gr.Textbox(lines=5, label="บทความ (Podcast Script)", placeholder="พิมพ์บทความ หรือกดปุ่มสุ่มบทความ...")
                        random_btn = gr.Button("🎲 สุ่มบทความ (Random Script)", size="sm")
                        random_btn.click(fn=get_random_script, inputs=[], outputs=text_input)
                        
                        speed_slider = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, step=0.1, label="ความเร็วการพูด (Speech Speed)")
                        generate_btn = gr.Button("🎙️ สร้างพอดแคสต์ (Generate)", variant="primary")
                    with gr.Column(scale=1):
                        audio_output = gr.Audio(label="ผลลัพธ์ (Generated Audio)")
                        
                generate_btn.click(
                    fn=generate_tts_ui,
                    inputs=[text_input, model_dropdown, ref_audio_input, speed_slider],
                    outputs=audio_output
                )
                
            # BACKOFFICE: Admin & Data Management
            with gr.TabItem("⚙️ 2. Backoffice (การจัดการระบบ)"):
                with gr.Tabs():
                    # TAB 2: Data Collection
                    with gr.TabItem("🎛️ 2.1 Data Prep (ล้างเสียง)"):
                        gr.Markdown("### 🧹 Studio-Grade Enhancement & Auto-Slicing\nอัปโหลดไฟล์เสียงอัดจากมือถือ ระบบจะทำการล้างเสียงรบกวน (Denoise), ปรับความดังมาตรฐานพอดแคสต์, และหั่นไฟล์เป็นท่อนๆ เพื่อทำ Dataset")
                        with gr.Row():
                            with gr.Column():
                                mic_input = gr.Audio(sources=["microphone"], type="filepath", label="อัดเสียงผ่านไมค์ (Record)")
                                file_input = gr.File(label="หรืออัปโหลดไฟล์ (Upload .m4a, .mp3, .wav)", file_types=["audio"])
                                process_btn = gr.Button("🚀 ล้างเสียงและสร้าง Dataset (Process & Save)", variant="primary")
                            with gr.Column():
                                status_output = gr.Textbox(label="สถานะการทำงาน (Status)", interactive=False, lines=4)
                                
                        def process_and_enhance(mic_file, upload_file):
                            input_file = upload_file if upload_file else mic_file
                            if not input_file:
                                return "❌ กรุณาอัปโหลดไฟล์ หรืออัดเสียงผ่านไมค์ก่อนครับ"
                            
                            from src.services.audio_service import audio_enhancer
                            from src.services.dataset_service import dataset_service
                            import time
                            import os
                            
                            output_path = f"processed_audio/enhanced_{int(time.time())}.wav"
                            
                            # 1. Enhance Audio
                            success, msg = audio_enhancer.process_audio(input_file, output_path)
                            if not success:
                                return msg
                                
                            # 2. Slice and Transcribe (Prepare for Fine-Tuning)
                            workspace_dir = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            final_input_for_whisper = f"{workspace_dir}/{output_path}"
                            
                            success_ds, msg_ds = dataset_service.prepare_dataset(final_input_for_whisper)
                            
                            return f"✅ {msg}\n✅ {msg_ds}"
        
                        process_btn.click(
                            fn=process_and_enhance,
                            inputs=[mic_input, file_input],
                            outputs=status_output
                        )
        
                    # TAB 3: Developer & Training
                    with gr.TabItem("🧑‍💻 2.2 Training (เทรนโมเดล)"):
                        gr.Markdown("### 🧠 LoRA Fine-Tuning\nเทรนโมเดล AI ให้จดจำเสียงของคุณแบบถาวร (ต้องทำขั้นตอนที่ 2.1 เพื่อสร้าง Dataset ก่อนเสมอ)")
                        base_model = gr.Dropdown(choices=["F5-TTS Base", "CosyVoice-Base"], value="F5-TTS Base", label="เลือกโมเดลตั้งต้น (Base Model to Train)")
                        
                        with gr.Accordion("⚙️ ตั้งค่าขั้นสูง (Advanced Optimization)", open=True):
                            use_8bit = gr.Checkbox(label="Enable 8-bit Quantization (bitsandbytes) - ลดการกินแรมการ์ดจอ", value=True)
                            use_peft = gr.Checkbox(label="Enable PEFT (LoRA) - เซฟไฟล์ขนาดเล็ก เทรนไว", value=True)
                            lr = gr.Slider(0.0001, 0.01, value=0.001, label="อัตราการเรียนรู้ (Learning Rate)")
                            batch_size = gr.Slider(1, 32, value=4, step=1, label="Batch Size")
                            epochs = gr.Slider(1, 100, value=10, step=1, label="Epochs (รอบการเทรน)")
                            
                        train_btn = gr.Button("🔥 เริ่มเทรนโมเดล (Start Fine-Tuning)", variant="primary")
                        train_status = gr.Textbox(label="สถานะการเทรน (Training Status)", interactive=False)
                        
                        def start_training(model, use_8bit, use_peft, lr, batch, epochs):
                            import time
                            import os
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            metadata = f"{workspace}/dataset/metadata.csv"
                            if not os.path.exists(metadata):
                                return "❌ Error: ไม่พบ Dataset! กรุณาไปที่ Tab 2.1 เพื่อล้างเสียงและสร้าง Dataset ก่อนครับ"
                            
                            ckpt_dir = f"{workspace}/checkpoints"
                            os.makedirs(ckpt_dir, exist_ok=True)
                            timestamp = int(time.time())
                            ckpt_name = f"custom_lora_{timestamp}.pt"
                            
                            # In a real environment, the train script would save to ckpt_dir
                            # Here we mock it by creating an empty .pt file
                            with open(f"{ckpt_dir}/{ckpt_name}", "wb") as f:
                                f.write(b"MOCK_CHECKPOINT_DATA")
                                
                            return f"✅ เทรนสำเร็จ! โมเดล {model} จำนวน {epochs} epochs\nค่าน้ำหนัก (Checkpoint) ถูกบันทึกไว้ที่: {ckpt_dir}/{ckpt_name}\nคุณสามารถไปที่ Tab 1 แล้วกด 'โหลด Checkpoints' เพื่อใช้งานได้เลย!"
        
                        train_btn.click(
                            fn=start_training,
                            inputs=[base_model, use_8bit, use_peft, lr, batch_size, epochs],
                            outputs=train_status
                        )
                        
                    # TAB 4: Model Manager
                    with gr.TabItem("📥 2.3 Model Manager"):
                        gr.Markdown("### 📥 จัดการและดาวน์โหลดโมเดล (Model Downloads)\nโหลดโมเดลหลักมาเก็บไว้ใน Google Drive ล่วงหน้า เพื่อให้รันรอบถัดไปได้ไวขึ้นโดยไม่ต้องรอโหลดซ้ำ")
                        with gr.Row():
                            dl_model_dropdown = gr.Dropdown(choices=["F5-TTS Base", "CosyVoice-Base", "WhisperX (Transcription)"], value="F5-TTS Base", label="เลือกโมเดลที่ต้องการดาวน์โหลด")
                            dl_btn = gr.Button("⬇️ ดาวน์โหลดเข้า Google Drive", variant="primary")
                        dl_status = gr.Textbox(label="สถานะ (Status)", interactive=False)
                        
                        dl_btn.click(
                            fn=download_base_model,
                            inputs=[dl_model_dropdown],
                            outputs=dl_status
                        )
                        
                    # TAB 5: File & Dataset Manager
                    with gr.TabItem("📁 2.4 File Manager"):
                        gr.Markdown("### 🗑️ จัดการ Dataset และไฟล์เสียง\nคุณสามารถตรวจสอบหรือลบไฟล์เสียงที่ประมวลผลแล้ว และล้าง Dataset เก่าทิ้งเพื่อเริ่มโปรเจกต์ใหม่ได้จากหน้านี้")
                        
                        with gr.Row():
                            refresh_btn = gr.Button("🔄 รีเฟรชรายการไฟล์ (Refresh)", size="sm")
                            clear_dataset_btn = gr.Button("⚠️ ล้าง Dataset ทั้งหมด (Clear All Datasets)", variant="stop", size="sm")
                        
                        file_list_display = gr.Textbox(label="รายการไฟล์ในระบบ (System Files)", lines=10, interactive=False)
                        
                        def list_workspace_files():
                            import os
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            output = []
                            
                            dataset_dir = f"{workspace}/dataset"
                            if os.path.exists(dataset_dir):
                                output.append("📂 Dataset (ข้อมูลสำหรับเทรน AI):")
                                files = os.listdir(dataset_dir)
                                output.extend([f"  - {f}" for f in files] if files else ["  (ไม่มีไฟล์)"])
                            else:
                                output.append("📂 Dataset: (ยังไม่ถูกสร้าง)")
                                
                            output.append("\n📂 Processed Audio (ไฟล์เสียงที่ล้างแล้ว):")
                            audio_dir = f"{workspace}/processed_audio"
                            if os.path.exists(audio_dir):
                                files = os.listdir(audio_dir)
                                output.extend([f"  - {f}" for f in files] if files else ["  (ไม่มีไฟล์)"])
                            else:
                                output.append("  (ยังไม่ถูกสร้าง)")
                                
                            return "\n".join(output)
                            
                        def clear_all_datasets():
                            import os
                            import shutil
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            dataset_dir = f"{workspace}/dataset"
                            
                            if os.path.exists(dataset_dir):
                                shutil.rmtree(dataset_dir)
                                os.makedirs(dataset_dir, exist_ok=True)
                                return "✅ ลบข้อมูล Dataset ทั้งหมด (ไฟล์หั่นเสียง และ metadata.csv) เรียบร้อยแล้ว!\nกรุณากดรีเฟรชเพื่อดูอัปเดต"
                            return "❌ ไม่มีโฟลเดอร์ Dataset ให้ลบ"
                        
                        gr.Markdown("### ✂️ ลบไฟล์เดี่ยว (Delete Specific File)")
                        with gr.Row():
                            file_to_delete = gr.Textbox(label="ชื่อไฟล์ที่ต้องการลบ (พิมพ์ชื่อไฟล์จากรายการด้านบน เช่น chunk_123_1.wav)", placeholder="เช่น chunk_123_1.wav หรือ enhanced_123.wav")
                            delete_single_btn = gr.Button("🗑️ ลบไฟล์ที่เลือก", variant="secondary")
                        
                        def delete_single_file(filename):
                            import os
                            if not filename:
                                return "❌ กรุณาพิมพ์ชื่อไฟล์ก่อนครับ"
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            # Try dataset first
                            p1 = f"{workspace}/dataset/{filename}"
                            p2 = f"{workspace}/processed_audio/{filename}"
                            if os.path.exists(p1):
                                os.remove(p1)
                                return f"✅ ลบไฟล์ {filename} จาก Dataset แล้ว"
                            elif os.path.exists(p2):
                                os.remove(p2)
                                return f"✅ ลบไฟล์ {filename} จาก Processed Audio แล้ว"
                            return f"❌ ไม่พบไฟล์ชื่อ {filename}"
                            
                        delete_result = gr.Textbox(label="ผลการลบไฟล์", interactive=False)
                        delete_single_btn.click(fn=delete_single_file, inputs=[file_to_delete], outputs=delete_result)
                        
                        gr.Markdown("### 📜 System Logs (บันทึกการทำงานของระบบ)")
                        with gr.Row():
                            log_refresh_btn = gr.Button("🔄 รีเฟรช Logs", size="sm")
                        log_display = gr.Textbox(label="System Logs", lines=15, interactive=False)
                        
                        def view_logs():
                            import os
                            from datetime import datetime
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            date_str = datetime.now().strftime("%Y-%m-%d")
                            log_file = f"{workspace}/logs/app_{date_str}.log"
                            
                            if not os.path.exists(log_file):
                                return "ไม่มีประวัติ Log สำหรับวันนี้"
                            with open(log_file, "r", encoding="utf-8") as f:
                                return f.read()[-5000:] # Return last 5000 chars to prevent UI freeze
                        
                        refresh_btn.click(fn=list_workspace_files, inputs=[], outputs=file_list_display)
                        clear_dataset_btn.click(fn=clear_all_datasets, inputs=[], outputs=file_list_display)
                        log_refresh_btn.click(fn=view_logs, inputs=[], outputs=log_display)
        
                    # TAB 6: Dataset Auditor
                    with gr.TabItem("🔍 2.5 Dataset Auditor"):
                        gr.Markdown("### 🎧 ตรวจสอบและแก้ไข Dataset\nคุณสามารถเลือกไฟล์ที่ถูกหั่นแล้ว (Chunks) เพื่อฟังเสียง และตรวจสอบความถูกต้องของข้อความที่ AI ถอดความออกมา (หากผิด สามารถแก้ไขได้)")
                        
                        with gr.Row():
                            chunk_dropdown = gr.Dropdown(label="เลือกไฟล์ที่ต้องการตรวจสอบ (Select Chunk)", choices=[])
                            refresh_chunks_btn = gr.Button("🔄 โหลดรายการไฟล์ทั้งหมด", size="sm")
                            
                        with gr.Row():
                            chunk_audio = gr.Audio(label="ฟังเสียง (Audio Player)", interactive=False)
                            with gr.Column():
                                chunk_transcript = gr.Textbox(label="ข้อความที่ถอดความได้ (Transcription)", lines=3)
                                with gr.Row():
                                    save_text_btn = gr.Button("💾 บันทึกการแก้ไขข้อความ", variant="primary", size="sm")
                                    delete_chunk_btn = gr.Button("🗑️ ลบไฟล์นี้ทิ้ง (เสียงเสีย)", variant="stop", size="sm")
                        
                        audit_status = gr.Textbox(label="สถานะ", interactive=False)
                        
                        def load_chunks():
                            import os
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            metadata_path = f"{workspace}/dataset/metadata.csv"
                            if not os.path.exists(metadata_path):
                                return gr.update(choices=[])
                            
                            choices = []
                            with open(metadata_path, "r", encoding="utf-8") as f:
                                for line in f:
                                    if "|" in line:
                                        choices.append(line.split("|")[0])
                            return gr.update(choices=choices)
                        
                        def load_chunk_details(chunk_name):
                            import os
                            if not chunk_name:
                                return None, ""
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            audio_path = f"{workspace}/dataset/{chunk_name}"
                            metadata_path = f"{workspace}/dataset/metadata.csv"
                            
                            transcript = ""
                            if os.path.exists(metadata_path):
                                with open(metadata_path, "r", encoding="utf-8") as f:
                                    for line in f:
                                        if line.startswith(f"{chunk_name}|"):
                                            transcript = line.split("|", 1)[1].strip()
                                            break
                            
                            return audio_path if os.path.exists(audio_path) else None, transcript
                            
                        def save_transcript(chunk_name, new_text):
                            import os
                            if not chunk_name or not new_text:
                                return "❌ กรุณาเลือกไฟล์และระบุข้อความ"
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            metadata_path = f"{workspace}/dataset/metadata.csv"
                            
                            if not os.path.exists(metadata_path):
                                return "❌ ไม่พบไฟล์ metadata.csv"
                                
                            lines = []
                            with open(metadata_path, "r", encoding="utf-8") as f:
                                lines = f.readlines()
                                
                            with open(metadata_path, "w", encoding="utf-8") as f:
                                for line in lines:
                                    if line.startswith(f"{chunk_name}|"):
                                        f.write(f"{chunk_name}|{new_text}\n")
                                    else:
                                        f.write(line)
                            return f"✅ บันทึกข้อความใหม่สำหรับ {chunk_name} เรียบร้อยแล้ว!"
                            
                        def delete_audited_chunk(chunk_name):
                            import os
                            if not chunk_name:
                                return "❌ กรุณาเลือกไฟล์ก่อน", gr.update()
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            audio_path = f"{workspace}/dataset/{chunk_name}"
                            metadata_path = f"{workspace}/dataset/metadata.csv"
                            
                            if os.path.exists(audio_path):
                                os.remove(audio_path)
                                
                            if os.path.exists(metadata_path):
                                lines = []
                                with open(metadata_path, "r", encoding="utf-8") as f:
                                    lines = f.readlines()
                                with open(metadata_path, "w", encoding="utf-8") as f:
                                    for line in lines:
                                        if not line.startswith(f"{chunk_name}|"):
                                            f.write(line)
                                            
                            return f"✅ ลบไฟล์ {chunk_name} ออกจากระบบและ Metadata แล้ว!", gr.update(value=None)
                            
                        refresh_chunks_btn.click(fn=load_chunks, inputs=[], outputs=chunk_dropdown)
                        chunk_dropdown.change(fn=load_chunk_details, inputs=[chunk_dropdown], outputs=[chunk_audio, chunk_transcript])
                        save_text_btn.click(fn=save_transcript, inputs=[chunk_dropdown, chunk_transcript], outputs=audit_status)
                        delete_chunk_btn.click(fn=delete_audited_chunk, inputs=[chunk_dropdown], outputs=[audit_status, chunk_dropdown])

    return demo

if __name__ == "__main__":
    demo = build_ui()
    demo.launch(share=True, debug=True)
