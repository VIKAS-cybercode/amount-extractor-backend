# ocr_pipeline_gemini.py
import re
from rapidfuzz import fuzz
import pytesseract
from PIL import Image
import google.generativeai as genai
import os



genai.configure(api_key="AIzaSyBhj_TIY1pIWhps-ArvaMi196pq8VUuvRU")

# OCR text normalization
def normalize_text(text):
    corrections = {
        'O': '0', 'o':'0',
        'l': '1', 'I':'1',
        '|':'1'
    }
    for k,v in corrections.items():
        text = text.replace(k,v)
    return text

# Extract numeric tokens with nearby context
def extract_numbers_with_context(text, window=5):
    tokens = []
    words = text.split()
    for i, word in enumerate(words):
        # Match numbers or percentages
        if re.match(r'^\d+\.?\d*%?$', word):
            context = ' '.join(words[max(0,i-window):i])
            tokens.append({'number': word, 'context': context})
    return tokens

# Classify numeric token using LLM context (MODIFIED FUNCTION)
def classify_amount(token):
    prompt = f"""
You are a financial amount extractor. Given the context text and a numeric value, 
classify it as one of: total_bill, paid, due, discount, other_amount.

Context: "{token['context']}"
Number: {token['number']}

Return only the type.
"""
    try:
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        
       
        response = model.generate_content(prompt)
        
        token_type = response.text.strip()
        
        
        if token_type not in ["total_bill", "paid", "due", "discount", "other_amount"]:
            token_type = "other_amount"
        return token_type
        
    except Exception as e:
        print("LLM classification error:", e)
        return "other_amount"

# Build final JSON output
def build_final_json(tokens, currency="INR"):
    amounts = []
    for t in tokens:
        amounts.append({
            "type": classify_amount(t),
            "value": float(t['number'].replace('%','')),
            "source": f"text: '{t['context']} {t['number']}'"
        })
    return {"currency": currency, "amounts": amounts, "status":"ok"}

# Full pipeline for text input
def process_text(text):
    text = normalize_text(text)
    tokens = extract_numbers_with_context(text)
    if not tokens:
        return {"status":"no_amounts_found","reason":"document too noisy"}
    return build_final_json(tokens)

# Full pipeline for image input
def process_image(file):
    try:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        return process_text(text)
    except Exception as e:
        print("OCR processing error:", e)
        return {"status":"no_amounts_found","reason":"OCR failed"}