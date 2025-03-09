import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = ""

    for page in doc:
        text = page.get_text("text")
        if text.strip():  # If text is found, use it
            extracted_text += text + "\n"
        else:  
            images = convert_from_path(pdf_path, first_page=page.number+1, last_page=page.number+1)
            for img in images:
                extracted_text += pytesseract.image_to_string(img) + "\n"

    return extracted_text.strip()


