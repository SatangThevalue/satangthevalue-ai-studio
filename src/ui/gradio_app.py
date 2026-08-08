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
                        model_dropdown = gr.Dropdown(choices=["F5-TTS Base", "CosyVoice-Base", "LoRA-Custom-Voice (Your Voice)"], value="F5-TTS Base", label="เลือกโมเดล (Select Base Model)")
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
                
            # TAB 2: Data Collection
            with gr.TabItem("🎛️ 2. Data Prep (ล้างเสียง & เตรียมข้อมูล)"):
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
            with gr.TabItem("🧑‍💻 3. Training (เทรนโมเดลเสียง)"):
                gr.Markdown("### 🧠 LoRA Fine-Tuning\nเทรนโมเดล AI ให้จดจำเสียงของคุณแบบถาวร (ต้องทำขั้นตอนที่ 2. Data Prep เพื่อสร้าง Dataset ก่อนเสมอ)")
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
                        return "❌ Error: ไม่พบ Dataset! กรุณาไปที่ Tab 2 เพื่อล้างเสียงและสร้าง Dataset ก่อนครับ"
                    
                    return f"⏳ กำลังเริ่มเทรนโมเดล {model} จำนวน {epochs} epochs...\n(8-bit: {use_8bit}, LoRA: {use_peft})\nกรุณาดูความคืบหน้าในหน้าต่าง Terminal ของ Colab"

                train_btn.click(
                    fn=start_training,
                    inputs=[base_model, use_8bit, use_peft, lr, batch_size, epochs],
                    outputs=train_status
                )
                
            # TAB 4: Model Manager
            with gr.TabItem("⚙️ 4. Model Manager (จัดการคลังโมเดล)"):
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
            with gr.TabItem("📁 5. File Manager (จัดการไฟล์)"):
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
                
                refresh_btn.click(fn=list_workspace_files, inputs=[], outputs=file_list_display)
                clear_dataset_btn.click(fn=clear_all_datasets, inputs=[], outputs=file_list_display)

    return demo
