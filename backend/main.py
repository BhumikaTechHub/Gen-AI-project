from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import shutil
import os

from model_loader import ask_model
from pdf_utils import extract_pdf_pages
from scoring import score_slide

from db import init_db, create_report, save_slide, get_reports

app = FastAPI()
latest_results = []

init_db()

# ==================================================
# CORS
# ==================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================================================
# ROOT
# ==================================================
@app.get("/")
def root():
    return {"message": "Backend Running"}

# ==================================================
# MULTI-AGENT PROMPTS & FALLBACK LOGIC
# ==================================================
def process_agent_response(instruction, text, agent_role):
    # 1. Initial call
    response = ask_model(instruction, text[:1000])
    response = response.strip() if response else ""
    
    # Check if empty or weak
    weak_keywords = ["no data", "no strong signals", "missing", "none", "n/a", "no information", "cannot infer"]
    is_weak = not response or any(w in response.lower() for w in weak_keywords) or len(response) < 15
    
    # 2. Fallback: Re-call with stronger prompt
    if is_weak:
        strong_prompt = f"""CRITICAL INSTRUCTION: The previous attempt failed. 
You MUST generate realistic {agent_role} insights for this startup.

Provide 3-4 bullet points covering standard {agent_role} metrics.
If exact data is missing, YOU MUST INFER logical investor-level insights based on the general context.
Do NOT return empty output.
Do NOT say 'no data'.
Bullet points only."""
        response = ask_model(strong_prompt, text[:1000])
        response = response.strip() if response else ""
        
        is_weak = not response or any(w in response.lower() for w in weak_keywords) or len(response) < 15
        
        # 3. Default meaningful insights if still weak
        if is_weak:
            if agent_role == "INVESTOR":
                response = "* Requires clearer articulation of investment potential.\n* Consider highlighting core strengths and team capabilities.\n* Ensure fundability metrics are explicitly stated."
            elif agent_role == "MARKET":
                response = "* TAM/SAM/SOM should be clearly defined to understand market scale.\n* Detail specific demand trends in the target industry.\n* Identify and elaborate on primary growth opportunities."
            elif agent_role == "PRODUCT":
                response = "* Value proposition needs to be more sharply defined.\n* Differentiation from competitors should be highlighted.\n* Core features must be aligned with user pain points."
            elif agent_role == "RISK":
                response = "* Identify primary execution and market risks.\n* Provide a clearer competitive landscape analysis.\n* Outline specific challenges and mitigation strategies."
            elif agent_role == "FINANCE":
                response = "* Revenue model and pricing strategy need clarification.\n* Unit economics should be explicitly detailed.\n* Ensure financial projections are realistic and included."
            else:
                response = f"* Standard {agent_role} metrics require further evaluation.\n* Additional details are needed to properly assess this section.\n* Recommend gathering more specific data to clarify."

    # Formatting check: Ensure it has bullet points
    if "-" not in response and "*" not in response and "•" not in response:
        lines = response.split('\n')
        response = '\n'.join([f"* {line.strip()}" for line in lines if line.strip()])

    return response

def get_agent_prompt(role, specifics):
    return f"""Generate realistic {role} insights for this startup.

Provide 3–4 bullet points covering:
{specifics}

If exact data is missing, infer logical investor-level insights.
Do NOT return empty output.
Bullet points only."""

def investor_agent(text):
    instruction = get_agent_prompt("INVESTOR", "* fundability\n* investment potential\n* key strengths")
    return process_agent_response(instruction, text, "INVESTOR")

def market_agent(text):
    instruction = get_agent_prompt("MARKET", "* market size (TAM/SAM/SOM if possible)\n* demand trends\n* growth potential")
    return process_agent_response(instruction, text, "MARKET")

def product_agent(text):
    instruction = get_agent_prompt("PRODUCT", "* value proposition\n* differentiation\n* key features")
    return process_agent_response(instruction, text, "PRODUCT")

def risk_agent(text):
    instruction = get_agent_prompt("RISK", "* potential risks\n* competition\n* execution challenges")
    return process_agent_response(instruction, text, "RISK")



# ==================================================
# UPLOAD + ANALYZE
# ==================================================
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    global latest_results

    allowed = (".pdf", ".pptx", ".png", ".jpg", ".jpeg")

    if not file.filename.lower().endswith(allowed):
        return {"error": "Unsupported file type"}

    os.makedirs("temp", exist_ok=True)
    path = f"temp/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    slides = extract_pdf_pages(path)
    results = []

    report_id = create_report(file.filename)

    for slide in slides:

        txt = slide["text"].strip()

        if len(txt) < 10:
            feedback = "Insufficient readable content on this slide."
            rewrite = "No rewrite available."
            score = 0

        else:
            # MULTI AGENTS
            investor = investor_agent(txt)
            market = market_agent(txt)
            product = product_agent(txt)
            risk = risk_agent(txt)
            finance = finance_agent(txt)

            # CLEAN STRUCTURED OUTPUT
            feedback = f"""
Investor:
{investor}

Market:
{market}

Product:
{product}

Risk:
{risk}

Finance:
{finance}
"""

            # STRONG REWRITE PROMPT
            rewrite = ask_model(
                """Act like a top startup founder.

Rewrite this into a powerful pitch:
- strong hook
- clear value proposition
- include numbers if possible
- investor-friendly tone
- max 4–5 lines

Output only final version.""",
                txt[:1000]
            )

            feedback = feedback[:5000]
            rewrite = rewrite[:2000]

            score = score_slide(txt)

        result = {
            "slide_no": slide["slide_no"],
            "text": txt,
            "score": score,
            "feedback": feedback,
            "rewrite": rewrite
        }

        results.append(result)

        save_slide(report_id, slide["slide_no"], score, feedback, rewrite)

    latest_results = results
    return {"slides": results}

# ==================================================
# REPORT HISTORY
# ==================================================
@app.get("/reports")
def reports():
    return {"reports": get_reports()}

# ==================================================
# DOWNLOAD REPORT
# ==================================================
@app.get("/download-report")
def download_report():

    global latest_results

    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import simpleSplit

    file_name = "Investor_Report.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)

    width, height = A4
    y = height - 50

    def clean(t):
        return t.replace("*", "").replace("#", "").strip() if t else ""

    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, y, "Pitch Deck Investor Report")
    y -= 30

    if not latest_results:
        c.drawString(40, y, "No data available.")
        c.save()
        return FileResponse(file_name)

    for slide in latest_results:

        if y < 150:
            c.showPage()
            y = height - 50

        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, f"Slide {slide['slide_no']} | Score {slide['score']}/100")
        y -= 20

        c.setFont("Helvetica", 10)

        for section in ["feedback", "rewrite"]:

            text = clean(slide[section])
            lines = simpleSplit(text, "Helvetica", 10, 500)

            for line in lines:
                if y < 50:
                    c.showPage()
                    y = height - 50
                c.drawString(40, y, line)
                y -= 14

        y -= 20

    c.save()
    return FileResponse(file_name)