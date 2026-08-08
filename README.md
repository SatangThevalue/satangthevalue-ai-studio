# 🎙️ SatangTheValue AI Studio

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)
![Gradio](https://img.shields.io/badge/Gradio-UI-orange.svg)

โปรเจกต์ **SatangTheValue AI Studio** เป็นแพลตฟอร์ม Web Application แบบ End-to-End สำหรับสร้างและปรับแต่งเสียงพอดแคสต์ด้วยปัญญาประดิษฐ์ (AI TTS) โดยถูกออกแบบมาให้ทำงานประสานกันระหว่างการล้างเสียงระดับสตูดิโอ การสร้าง Dataset อัตโนมัติ และการจำลองโมเดลเสียงขั้นสูง (F5-TTS, CosyVoice)

โปรเจกต์นี้ถูกปรับแต่ง (Optimized) มาให้ทำงานบน **Google Colab** ได้อย่างสมบูรณ์แบบ โดยใช้หลักการ **Stateless Code, Stateful Data** ข้อมูลสำคัญทั้งหมดจะถูกซิงค์เข้า Google Drive อัตโนมัติ ทำให้คุณไม่ต้องกลัวข้อมูลสูญหายเมื่อปิดเบราว์เซอร์

---

## ✨ ฟีเจอร์หลัก (Key Features)

### 1. 🎧 การสร้างเสียงพอดแคสต์ (TTS Generation & Zero-Shot)
* รองรับ Base Model ทรงพลังที่ใช้งานเชิงพาณิชย์ได้ฟรี (F5-TTS, CosyVoice)
* **Zero-Shot Cloning:** เพียงอัปโหลดเสียงต้นฉบับความยาว 10 วินาที AI จะสามารถเลียนแบบน้ำเสียงและจังหวะการพูดของคุณเพื่อสร้างพอดแคสต์ตอนใหม่ได้ทันที

### 2. 🎛️ การล้างเสียงระดับสตูดิโอ (Studio-Grade Audio Enhancement)
* เปลี่ยนไฟล์เสียงอัดจากมือถือ (ที่ก้องและมีเสียงรบกวน) ให้กลายเป็นเสียงพอดแคสต์ระดับมืออาชีพ
* ใช้ `pedalboard` ทำ Highpass Filter, Podcast EQ, และ Compressor
* ปรับระดับความดังมาตรฐานพอดแคสต์ที่ **-14 LUFS** ผ่าน `pyloudnorm`
* รองรับไฟล์หลากหลายนามสกุลรวมถึง `.m4a` (ประมวลผลผ่าน `librosa` และ `ffmpeg`)

### 3. 🤖 การจัดการ Dataset อัตโนมัติ (Automated Dataset Prep)
* หั่นไฟล์เสียงยาวๆ ออกเป็นท่อนสั้น (3-10 วินาที)
* ถอดความคำพูด (Transcription) อัตโนมัติ และสร้างไฟล์ `metadata.csv` เพื่อเตรียมพร้อมสำหรับการเทรนโมเดล AI ในอนาคต
* ทำงานแบบ Incremental (สะสมยอด) สามารถอัปโหลดเสียงวันละนิดเพื่อสะสมข้อมูลได้โดยไม่ทับซ้อนกัน

### 4. 🧠 พร้อมสำหรับการ Fine-Tuning (LoRA & 8-bit)
* สถาปัตยกรรมรองรับการเทรนผ่าน `peft` (LoRA) และ `bitsandbytes` (8-bit Quantization) ช่วยประหยัด VRAM ของการ์ดจอบน Colab
* ตรรกะ Guardrail ป้องกันการกดเทรนหากยังไม่ได้เตรียม Dataset

---

## 🚀 วิธีการใช้งานบน Google Colab (แนะนำ)

1. คลิกเพื่อเปิดไฟล์ `colab_runner.ipynb` บน Google Colab
2. ตั้งค่ารันไทม์เป็น **T4 GPU**
3. กด **Run All**
4. ระบบจะทำการ:
   * ดึงโค้ดเวอร์ชันล่าสุดจาก GitHub
   * สร้าง Workspace ชื่อ `satangthevalue-ai-studio` ใน Google Drive ของคุณ
   * ติดตั้งไลบรารีที่จำเป็นผ่าน `uv` (เร็วมาก)
   * รันเซิร์ฟเวอร์ FastAPI และสร้างลิงก์ **Localtunnel** ให้คุณคลิกเข้าใช้งานผ่านเบราว์เซอร์

---

## 💻 การติดตั้งบนเครื่องคอมพิวเตอร์ (Local Development)

หากต้องการรันโปรเจกต์นี้บนคอมพิวเตอร์ของคุณเอง (ต้องมี GPU NVIDIA):

```bash
# 1. โคลนโปรเจกต์
git clone https://github.com/SatangThevalue/satangthevalue-ai-studio.git
cd satangthevalue-ai-studio

# 2. ติดตั้ง Dependencies ด้วย uv
pip install uv
uv pip install -r pyproject.toml

# 3. รันระบบ
uvicorn src.main:app --host 0.0.0.0 --port 8000
```
จากนั้นเปิดเบราว์เซอร์ไปที่ `http://localhost:8000`

---

## 📂 โครงสร้างโปรเจกต์ (Project Structure)

```text
satangthevalue-ai-studio/
├── src/
│   ├── api/            # FastAPI Routers
│   ├── services/       # ตรรกะหลังบ้าน (Audio, TTS, Dataset)
│   ├── ui/             # หน้าตาเว็บ Gradio
│   ├── database.py     # ระบบฐานข้อมูล SQLite
│   └── main.py         # จุดเริ่มต้น (Entry point) เชื่อม FastAPI + Gradio
├── docs/               # เอกสารประกอบโครงการ (Architecture, Workflow)
├── pyproject.toml      # รายการ Library ที่โปรเจกต์ใช้งาน
├── colab_runner.ipynb  # ไฟล์สำหรับรันบน Google Colab (E2E)
└── README.md           # ไฟล์นี้
```

---

## 📜 ลิขสิทธิ์ (License)
โปรเจกต์นี้ใช้ไลเซนส์ MIT (คุณสามารถนำไปปรับใช้เชิงพาณิชย์ได้ฟรี) อย่างไรก็ตาม กรุณาตรวจสอบไลเซนส์ของโมเดล AI แต่ละตัว (เช่น F5-TTS) ก่อนนำไปใช้ทำธุรกิจจริง
