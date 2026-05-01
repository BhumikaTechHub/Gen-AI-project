'''import fitz
def extract_pdf_pages(file_path):

    doc = fitz.open(file_path)
    slides = []

    for i, page in enumerate(doc):

        text = page.get_text("text")

        if not text.strip():
            text = page.get_text("blocks")
            text = str(text)
 
        slides.append({
            "slide_no": i + 1,
            "text": text.strip()
        })

    return slides'''

# backend/pdf_utils.py
# Handles PDFs, PPT/PPTX exported PDFs, image-based docs, scanned docs

import fitz
import pytesseract
from PIL import Image
import io
import os

# ---------------------------------------------------
# WINDOWS USERS (uncomment if needed)
# ---------------------------------------------------
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------------------------------------------
# MAIN EXTRACT FUNCTION
# ---------------------------------------------------

def extract_pdf_pages(file_path):

    doc = fitz.open(file_path)
    slides = []

    for i, page in enumerate(doc):

        extracted_text = ""

        # ==========================================
        # METHOD 1 -> NORMAL TEXT EXTRACTION
        # ==========================================
        try:
            extracted_text = page.get_text("text").strip()
        except:
            extracted_text = ""

        # ==========================================
        # METHOD 2 -> BLOCK EXTRACTION
        # ==========================================
        if len(extracted_text) < 20:
            try:
                blocks = page.get_text("blocks")
                block_text = " ".join(
                    [b[4].strip() for b in blocks if len(b) > 4]
                )
                extracted_text = block_text.strip()
            except:
                pass

        # ==========================================
        # METHOD 3 -> OCR IMAGE EXTRACTION
        # ==========================================
        if len(extracted_text) < 20:
            try:
                pix = page.get_pixmap(dpi=250)
                img_bytes = pix.tobytes("png")

                img = Image.open(io.BytesIO(img_bytes))

                extracted_text = pytesseract.image_to_string(img).strip()
            except:
                pass

        # ==========================================
        # CLEAN TEXT
        # ==========================================
        extracted_text = clean_text(extracted_text)

        # ==========================================
        # DEFAULT FALLBACK
        # ==========================================
        if len(extracted_text) == 0:
            extracted_text = "No readable content found."

        slides.append({
            "slide_no": i + 1,
            "text": extracted_text
        })

    return slides


# ---------------------------------------------------
# CLEAN TEXT
# ---------------------------------------------------

def clean_text(text):

    if not text:
        return ""

    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")

    while "  " in text:
        text = text.replace("  ", " ")

    return text.strip()