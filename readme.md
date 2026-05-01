#  Pitch Deck AI Analyzer

An AI-powered startup pitch deck analysis platform that allows users to upload pitch decks (PDF, PPT, images, documents), automatically extract slide content, score each slide, generate investor-style feedback, rewrite weak slides, and download an investor report.

---

#  Features

##  Upload Pitch Deck Files
Supports:

- PDF files
- PowerPoint slides
- Images
- Documents

---

## AI Slide Analysis

Each slide is automatically analyzed using a fine-tuned LLM.

Outputs:

- Slide Score (/100)
- Investor Feedback
- Strengths
- Weaknesses
- Improvement Suggestions
- Stronger Rewrite Version

---

##  Smart Scoring Engine

Slides are scored based on:

- Business clarity
- Revenue model
- Market size
- Traction
- Team quality
- Financial metrics
- Fundraising readiness

---

##  Download Investor Report

Generate downloadable PDF report containing:

- Slide-wise scores
- Feedback
- Rewrites
- Overall deck score

---

#  AI Model Used

## Base Model:

Qwen/Qwen2.5-1.5B-Instruct

## Fine-Tuning:

PEFT / LoRA fine-tuning on custom startup + finance + business dataset.

---

#  Tech Stack

## Frontend

- React.js
- Axios
- CSS / Inline UI Styling

## Backend

- FastAPI
- Python
- PyMuPDF
- ReportLab

## AI / ML

- HuggingFace Transformers
- PEFT / LoRA
- Fine-Tuned Qwen Model

---

# Project Structure

```bash
startup-ai-project/
│── frontend/
│── backend/
│── datasets/
│── reports/
│── README.md
```



## Backend Setup

```cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```
Backend runs on:
```
http://127.0.0.1:8000
```
## Frontend Setup
```
cd frontend
npm install
npm run dev
```
Frontend runs on:
```
http://localhost:5173

```
