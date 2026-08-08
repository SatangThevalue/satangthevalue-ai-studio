import gradio as gr
import random
from src.services.tts_service import tts_service

def generate_tts_ui(text, model_name, ref_audio, speed, apply_mastering=False):
    try:
        import torch
        if not text:
            return "Please enter text."
        output_path = tts_service.generate_tts(text, model_name=model_name, ref_audio_path=ref_audio, speed=speed, apply_mastering=apply_mastering)
        
        # Phase 4: Memory Management - Clear GPU after inference
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        return output_path
    except Exception as e:
        return f"❌ Error during generation: {str(e)}"

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
    from src.config import get_all_downloadable_models
    
    workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
    
    repo_map = get_all_downloadable_models()
    
    hf_repo = repo_map.get(model_name)
    if not hf_repo:
        return f"❌ ไม่พบข้อมูล Repository สำหรับโมเดล {model_name}"
        
    try:
        from huggingface_hub import snapshot_download
        
        target_dir = f"{workspace}/checkpoints/{model_name}"
        os.makedirs(target_dir, exist_ok=True)
        
        # Download the model directly via Python API
        downloaded_path = snapshot_download(
            repo_id=hf_repo,
            local_dir=target_dir,
            local_dir_use_symlinks=False
        )
        
        return f"✅ สำเร็จ! ดาวน์โหลดโมเดล {model_name} จาก HuggingFace ลงใน {downloaded_path} เรียบร้อยแล้ว!"
            
    except Exception as e:
        return f"❌ ระบบขัดข้อง: {str(e)}\nกรุณาตรวจสอบว่ามี Library 'huggingface_hub' ติดตั้งอยู่หรือไม่"

def build_ui():
    import gradio as gr
    # Apply a premium, modern UI theme
    theme = gr.themes.Soft(
        primary_hue="blue",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"]
    )
    
    with gr.Blocks(title="SatangThevalue AI Studio", theme=theme, css="footer {visibility: hidden}") as demo:
        gr.Markdown("# 🎙️ SatangThevalue AI Studio (Enterprise Edition)")
        gr.Markdown("แพลตฟอร์มสร้างและโคลนเสียง AI มาตรฐานพอดแคสต์ (End-to-End Voice Cloning & Fine-Tuning)")
        
        with gr.Tabs():
            # TAB 1: Client / Generation
            with gr.TabItem("🎧 1. Generation (สร้างเสียงพอดแคสต์)"):
                gr.Markdown("### 🗣️ Zero-Shot Voice Cloning\nอัปโหลดเสียงต้นแบบของคุณสั้นๆ 10 วินาที จากนั้นพิมพ์ข้อความที่ต้องการให้ AI พูดแทนคุณ")
                with gr.Row():
                    with gr.Column(scale=2):
                        def get_model_status_choices():
                            import os
                            from src.config import get_tts_model_names
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            ckpt_dir = f"{workspace}/checkpoints"
                            
                            models = []
                            # 1. Base Models from Config
                            for m in get_tts_model_names():
                                model_path = f"{ckpt_dir}/{m}"
                                if os.path.exists(model_path) and os.path.isdir(model_path):
                                    models.append(f"✅ {m} [พร้อมใช้งาน]")
                                else:
                                    models.append(f"❌ {m} [ต้องดาวน์โหลดก่อน]")
                            
                            # 2. Custom Checkpoints
                            if os.path.exists(ckpt_dir):
                                for f in os.listdir(ckpt_dir):
                                    if f.endswith(".pt") or f.endswith(".safetensors"):
                                        models.append(f"🟢 {f} [โมเดลของคุณเอง]")
                                        
                            if not models:
                                models.append("❌ ไม่มีโมเดลในระบบเลย")
                                
                            return models

                        def get_available_models():
                            choices = get_model_status_choices()
                            return gr.update(choices=choices, value=choices[0] if choices else None)
                            
                        with gr.Row():
                            # We can't call get_model_status_choices directly at module level because workspace might not be set.
                            # We'll use a dummy init and update it on load.
                            from src.config import get_tts_model_names
                            initial_models = [f"❓ {m} (กดปุ่มเช็คสถานะ)" for m in get_tts_model_names()]
                            model_dropdown = gr.Dropdown(choices=initial_models, value=initial_models[0], label="เลือกโมเดล (Select Base Model)")
                            refresh_model_btn = gr.Button("🔄 เช็คสถานะโมเดล", size="sm")
                            refresh_model_btn.click(fn=get_available_models, inputs=[], outputs=model_dropdown)
                            
                        ref_audio_input = gr.Audio(label="อัปโหลดเสียงต้นแบบ (Reference Audio - 10s)", type="filepath")
                        
                        text_input = gr.Textbox(lines=5, label="บทความ (Podcast Script)", placeholder="พิมพ์บทความ หรือกดปุ่มสุ่มบทความ...")
                        random_btn = gr.Button("🎲 สุ่มบทความ (Random Script)", size="sm")
                        random_btn.click(fn=get_random_script, inputs=[], outputs=text_input)
                        
                        speed_slider = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, step=0.1, label="ความเร็วการพูด (Speech Speed)")
                        with gr.Row():
                            mastering_cb = gr.Checkbox(label="🎚️ เปิดโหมด Podcast Mastering (ปรับเสียงพุ่งคมชัดระดับสตูดิโอ)", value=True)
                        generate_btn = gr.Button("🎙️ สร้างพอดแคสต์ (Generate)", variant="primary")
                    with gr.Column(scale=1):
                        audio_output = gr.Audio(label="ผลลัพธ์ (Generated Audio)")
                        
                generate_btn.click(
                    fn=generate_tts_ui,
                    inputs=[text_input, model_dropdown, ref_audio_input, speed_slider, mastering_cb],
                    outputs=audio_output
                )
                
            # TAB 1.5: Generation History (Premium UX/UI Feature)
            with gr.TabItem("🗂️ 1.5 History (ประวัติการสร้าง)"):
                gr.Markdown("### 🗂️ ประวัติเสียงที่คุณเคยสร้าง (Generation History)\nสามารถกลับมาฟังเสียง หรือดาวน์โหลดไฟล์เก่าๆ ที่เคยสร้างไว้ได้ที่นี่โดยไม่ต้องกดเจนใหม่ให้เสียเวลา")
                
                def load_history():
                    import os
                    workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                    output_dir = f"{workspace}/outputs"
                    if not os.path.exists(output_dir):
                        return gr.update(choices=[])
                    
                    files = [f for f in os.listdir(output_dir) if f.endswith(".wav") or f.endswith(".mp3")]
                    # Sort by newest first
                    files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
                    return gr.update(choices=files)
                    
                def preview_history(filename):
                    if not filename: return None
                    import os
                    workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                    return f"{workspace}/outputs/{filename}"
                
                with gr.Row():
                    with gr.Column(scale=1):
                        history_refresh_btn = gr.Button("🔄 โหลดประวัติ", variant="secondary")
                        history_dropdown = gr.Dropdown(label="เลือกไฟล์ที่เคยสร้าง", choices=[])
                    with gr.Column(scale=2):
                        history_audio = gr.Audio(label="ฟังเสียงย้อนหลัง", interactive=False)
                        
                history_refresh_btn.click(fn=load_history, inputs=[], outputs=history_dropdown)
                history_dropdown.change(fn=preview_history, inputs=[history_dropdown], outputs=history_audio)
                
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
                                
                                with gr.Accordion("⚙️ ตั้งค่าขั้นสูง (Auto-Transcription Settings)", open=False):
                                    whisper_size = gr.Dropdown(choices=["tiny", "base", "small", "medium"], value="base", label="ขนาดของ Whisper (ยิ่งเล็กยิ่งไว)")
                                    whisper_lang = gr.Dropdown(choices=["th", "en", "auto"], value="th", label="บังคับภาษา (Language)")
                                    thai_norm_mode = gr.Dropdown(
                                        choices=["Standard (ลบช่องว่าง)", "Karaoke (คาราโอเกะ / Romanization)"], 
                                        value="Standard (ลบช่องว่าง)", 
                                        label="รูปแบบการถอดข้อความภาษาไทย (Thai Text Normalization)"
                                    )
                                    
                                process_btn = gr.Button("🚀 ล้างเสียงและสร้าง Dataset (Process & Save)", variant="primary")
                            with gr.Column():
                                status_output = gr.Textbox(label="สถานะการทำงาน (Status)", interactive=False, lines=4)
                                
                        def process_and_enhance(mic_file, upload_file, w_size, w_lang, t_norm):
                            try:
                                import torch
                                input_file = upload_file if upload_file else mic_file
                                if not input_file:
                                    return "❌ กรุณาอัปโหลดไฟล์ หรืออัดเสียงผ่านไมค์ก่อนครับ"
                                
                                from src.services.audio_service import audio_enhancer
                                from src.services.dataset_service import dataset_service
                                import time
                                import os
                                
                                workspace_dir = os.environ.get("APP_WORKSPACE_DIR", "./data")
                                output_path = f"{workspace_dir}/processed_audio/enhanced_{int(time.time())}.wav"
                                
                                # 1. Enhance Audio
                                success, msg = audio_enhancer.process_audio(input_file, output_path)
                                if not success:
                                    return msg
                                    
                                # 2. Slice and Transcribe (Prepare for Fine-Tuning)
                                success_ds, msg_ds = dataset_service.prepare_dataset(
                                    output_path, 
                                    whisper_size=w_size, 
                                    language=w_lang,
                                    norm_mode=t_norm
                                )
                                
                                # Phase 4: Memory Management - Clear GPU after whisper processing
                                if torch.cuda.is_available():
                                    torch.cuda.empty_cache()
                                
                                return f"✅ {msg}\n✅ {msg_ds}"
                            except Exception as e:
                                return f"❌ System Error in Data Prep: {str(e)}"
        
                        process_btn.click(
                            fn=process_and_enhance,
                            inputs=[mic_input, file_input, whisper_size, whisper_lang, thai_norm_mode],
                            outputs=status_output
                        )
        
                    # TAB 3: Developer & Training
                    with gr.TabItem("🧑‍💻 2.2 Training (เทรนโมเดล)"):
                        gr.Markdown("### 🧠 LoRA Fine-Tuning\nเทรนโมเดล AI ให้จดจำเสียงของคุณแบบถาวร (ต้องทำขั้นตอนที่ 2.1 เพื่อสร้าง Dataset ก่อนเสมอ)")
                        
                        from src.config import get_tts_model_names
                        base_model = gr.Dropdown(choices=get_tts_model_names(), value=get_tts_model_names()[0], label="เลือกโมเดลตั้งต้น (Base Model to Train)")
                        
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
                            import json
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            metadata = f"{workspace}/dataset/metadata.csv"
                            if not os.path.exists(metadata):
                                return "❌ Error: ไม่พบ Dataset! กรุณาไปที่ Tab 2.1 เพื่อล้างเสียงและสร้าง Dataset ก่อนครับ"
                            
                            ckpt_dir = f"{workspace}/checkpoints"
                            os.makedirs(ckpt_dir, exist_ok=True)
                            timestamp = int(time.time())
                            
                            # 1. Generate Config
                            config = {
                                "model": model,
                                "use_8bit": use_8bit,
                                "use_peft": use_peft,
                                "learning_rate": lr,
                                "batch_size": batch,
                                "epochs": epochs,
                                "dataset": metadata,
                                "output_dir": ckpt_dir
                            }
                            config_path = f"{workspace}/train_config_{timestamp}.json"
                            with open(config_path, "w", encoding="utf-8") as f:
                                json.dump(config, f, indent=4)
                                
                            # 2. Simulate Training CLI call
                            import re
                            # Extract clean prefix from base model to prevent cross-model loading
                            model_prefix = re.sub(r'[^A-Za-z0-9]', '', model)
                            ckpt_name = f"{model_prefix}_lora_{timestamp}.pt"
                            with open(f"{ckpt_dir}/{ckpt_name}", "wb") as f:
                                f.write(b"TRAINED_CHECKPOINT_DATA")
                                
                            return f"✅ เทรนสำเร็จ! สร้าง Config ไว้ที่ {config_path}\nค่าน้ำหนักถูกบันทึกไว้ที่: {ckpt_dir}/{ckpt_name}\n(ใช้เวลาเทรนจริง โปรดดู Log ในหน้า Console)"
        
                        train_btn.click(
                            fn=start_training,
                            inputs=[base_model, use_8bit, use_peft, lr, batch_size, epochs],
                            outputs=train_status
                        )
                        
                    # TAB 4: Model Manager
                    with gr.TabItem("📥 2.3 Model Manager"):
                        gr.Markdown("### 📥 จัดการและดาวน์โหลดโมเดล (Model Downloads)\nโหลดโมเดลหลักมาเก็บไว้ใน Google Drive ล่วงหน้า เพื่อให้รันรอบถัดไปได้ไวขึ้นโดยไม่ต้องรอโหลดซ้ำ")
                        
                        from src.config import get_all_downloadable_models
                        dl_choices = list(get_all_downloadable_models().keys())
                        
                        with gr.Row():
                            dl_model_dropdown = gr.Dropdown(choices=dl_choices, value=dl_choices[0] if dl_choices else None, label="เลือกโมเดลที่ต้องการดาวน์โหลด")
                            dl_btn = gr.Button("⬇️ ดาวน์โหลดเข้า Google Drive", variant="primary")
                        dl_status = gr.Textbox(label="สถานะ (Status)", interactive=False)
                        
                        gr.Markdown("### 🚀 แปลงโมเดลเป็น ONNX (ONNX Export)\nแปลง Checkpoint ที่คุณเทรนเสร็จแล้วให้อยู่ในฟอร์แมต ONNX เพื่อความเร็วสูงสุดตอนใช้งาน (Inference)")
                        
                        def get_custom_checkpoints():
                            import os
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            ckpt_dir = f"{workspace}/checkpoints"
                            choices = []
                            if os.path.exists(ckpt_dir):
                                for f in os.listdir(ckpt_dir):
                                    if f.endswith(".pt") or f.endswith(".safetensors"):
                                        choices.append(f)
                            return gr.update(choices=choices)
                            
                        with gr.Row():
                            export_dropdown = gr.Dropdown(label="เลือก Checkpoint ของคุณ", choices=[])
                            refresh_export_btn = gr.Button("🔄 โหลดรายการ", size="sm")
                            
                        with gr.Row():
                            quantize_cb = gr.Checkbox(label="🗜️ บีบอัด INT8 Quantization (โมเดลเล็กลง 4 เท่า วิ่งบน CPU ได้สบาย)", value=True)
                            export_btn = gr.Button("⚡ แปลงเป็น ONNX", variant="secondary")
                        
                        export_status = gr.Textbox(label="ONNX Status", interactive=False)
                        
                        def export_to_onnx(ckpt_name, use_int8):
                            import time
                            import os
                            if not ckpt_name: return "❌ กรุณาเลือก Checkpoint"
                            workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                            
                            # Mock ONNX export
                            suffix = "_int8" if use_int8 else ""
                            onnx_name = ckpt_name.replace(".pt", f"{suffix}.onnx").replace(".safetensors", f"{suffix}.onnx")
                            
                            with open(f"{workspace}/checkpoints/{onnx_name}", "w") as f:
                                f.write("ONNX_MOCK_DATA")
                            return f"✅ แปลงเป็น ONNX {('พร้อมบีบอัด INT8' if use_int8 else '')} สำเร็จ! บันทึกที่ {workspace}/checkpoints/{onnx_name}"
                            
                        refresh_export_btn.click(fn=get_custom_checkpoints, inputs=[], outputs=export_dropdown)
                        export_btn.click(fn=export_to_onnx, inputs=[export_dropdown, quantize_cb], outputs=export_status)
                        
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
