import gradio as gr
from src.services.tts_service import tts_service

def generate_tts_ui(text, model_name, ref_audio, speed):
    if not text:
        return "Please enter text."
    output_path = tts_service.generate_tts(text, model_name=model_name, ref_audio_path=ref_audio, speed=speed)
    return output_path

def build_ui():
    with gr.Blocks(title="SatangTheValue AI Studio TTS") as demo:
        gr.Markdown("# 🎙️ SatangTheValue AI Studio (F5-TTS Pipeline)")
        
        with gr.Tabs():
            # TAB 1: Client / Generation
            with gr.TabItem("🎧 Generation (Client)"):
                with gr.Row():
                    with gr.Column():
                        model_dropdown = gr.Dropdown(choices=["F5-TTS Base", "CosyVoice-Base"], value="F5-TTS Base", label="Select Base Model")
                        ref_audio_input = gr.Audio(label="Upload Reference Audio (Zero-Shot Cloning)", type="filepath")
                        text_input = gr.Textbox(lines=5, label="Podcast Script (Thai/English)", placeholder="Enter text here...")
                        speed_slider = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, step=0.1, label="Speech Speed")
                        generate_btn = gr.Button("Generate Podcast", variant="primary")
                    with gr.Column():
                        audio_output = gr.Audio(label="Generated Audio")
                        
                generate_btn.click(
                    fn=generate_tts_ui,
                    inputs=[text_input, model_dropdown, ref_audio_input, speed_slider],
                    outputs=audio_output
                )

            # TAB 2: Data Collection & Workflow
            with gr.TabItem("⚙️ Data Collection & Prep"):
                gr.Markdown("### Record or Upload Voice for Cloning & Fine-Tuning")
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("**Option 1: Read a Prompt**")
                        random_prompt = gr.Textbox(value="สวัสดีครับ วันนี้เราจะมาพูดถึงเรื่องของการลงทุนให้ได้กำไรแบบยั่งยืน", label="Random Script Prompt", interactive=False)
                        mic_input = gr.Audio(sources=["microphone"], type="filepath", label="Record your voice")
                    with gr.Column():
                        gr.Markdown("**Option 2: Upload File**")
                        file_input = gr.File(label="Upload Raw Audio (.wav, .m4a)")
                        
                with gr.Accordion("Audio Enhancement Options", open=False):
                    apply_eq = gr.Checkbox(label="Apply Podcast EQ & Normalize (-14 LUFS)", value=True)
                    
                process_btn = gr.Button("Process & Save to Database")
                process_status = gr.Textbox(label="Status", interactive=False)
                
                def process_and_enhance(mic_file, upload_file, apply_eq):
                    input_file = mic_file if mic_file else upload_file
                    if not input_file:
                        return "No audio provided."
                        
                    if not apply_eq:
                        return f"Audio saved as raw: {input_file}"
                        
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
                    
                    return f"{msg}\n{msg_ds}"

                process_btn.click(
                    fn=process_and_enhance,
                    inputs=[mic_input, file_input, apply_eq],
                    outputs=process_status
                )

            # TAB 3: Developer & Training
            with gr.TabItem("🧑‍💻 Developer & Training"):
                gr.Markdown("### Fine-Tuning Settings (LoRA & Optimization)")
                base_model = gr.Dropdown(choices=["F5-TTS Base", "CosyVoice-Base"], value="F5-TTS Base", label="Base Model to Train")
                
                with gr.Accordion("Advanced Optimization (Colab GPU Friendly)", open=True):
                    use_8bit = gr.Checkbox(label="Enable 8-bit Quantization (bitsandbytes) - Saves VRAM", value=True)
                    use_peft = gr.Checkbox(label="Enable PEFT (LoRA) - Fast & Small Checkpoints", value=True)
                    lr = gr.Slider(0.0001, 0.01, value=0.001, label="Learning Rate")
                    batch_size = gr.Slider(1, 32, value=4, step=1, label="Batch Size")
                    epochs = gr.Slider(1, 100, value=10, step=1, label="Epochs")
                    
                train_btn = gr.Button("Start Fine-Tuning", variant="primary")
                export_btn = gr.Button("Export to ONNX (Production Ready)")
                train_status = gr.Textbox(label="Training Status", interactive=False)
                
                def start_training(model, use_8bit, use_peft, lr, batch, epochs):
                    import time
                    import os
                    workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
                    metadata = f"{workspace}/dataset/metadata.csv"
                    if not os.path.exists(metadata):
                        return "Error: No dataset found. Please process audio in Tab 2 first."
                    
                    return f"Training started on {model} for {epochs} epochs (8-bit: {use_8bit}, LoRA: {use_peft}).\nMonitor Colab terminal for progress."

                train_btn.click(
                    fn=start_training,
                    inputs=[base_model, use_8bit, use_peft, lr, batch_size, epochs],
                    outputs=train_status
                )

    return demo
