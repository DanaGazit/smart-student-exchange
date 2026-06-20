import os
import json
import base64
from io import BytesIO
from PIL import Image
import fitz  # PyMuPDF
from groq import Groq

def analyze_document(file_bytes: bytes, file_ext: str) -> dict:
    """
    מקבלת קובץ (תמונה או PDF), ממירה אותו לפורמט הנדרש, 
    שולחת ל-Groq AI ומחזירה מילון (dict) עם הנתונים שחולצו.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("Groq API Key is missing from environment variables.")
        
    groq_client = Groq(api_key=groq_api_key)

    # --- טיפול בקובץ (PDF או תמונה) ---
    if file_ext == 'pdf':
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        first_page = pdf_document.load_page(0)
        pix = first_page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # type: ignore
        pdf_document.close()
    else:
        img = Image.open(BytesIO(file_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
    # כיווץ והכנה ל-API
    img.thumbnail((1500, 1500)) 
    buffered = BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    clean_image_bytes = buffered.getvalue()
    
    base64_image = base64.b64encode(clean_image_bytes).decode('utf-8')
    
    # --- בניית הפרומפט וקריאה ל-AI ---
    prompt = """
    Analyze this document or image of a student's study material.
    Return ONLY a valid JSON object with the exact following keys and string values:
    - course_name: the precise name of the academic course in Hebrew. Read the text carefully.
    - topic: the specific topic of this page, written in Hebrew.
    - material_type: classify exactly as 'סיכום', 'מבחן', 'שיעורי בית', or 'דף נוסחאות'.
    - year: the academic year written (e.g., '2023', '2024', 'תשפ"ד'). If not found, write 'לא צוין'.
    - semester: the semester written (e.g., 'א', 'ב', 'קיץ'). If not found, write 'לא צוין'.
    - lecturer: the name of the lecturer if written. If not found, leave empty string "".
    - material_format: classify as 'מודפס' (typed) or 'בכתב יד' (handwritten). If unsure, leave empty "".
    Do not include any markdown formatting like ```json.
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct", 
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            temperature=0,
        )
        
        safe_text = response.choices[0].message.content or "{}"
        safe_text = safe_text.replace('```json', '').replace('```', '').strip()
        
        # מוודאים שהתשובה היא אכן במבנה של JSON
        if not safe_text.startswith('{') or not safe_text.endswith('}'):
            raise ValueError("ה-AI התקשה לפענח את המסמך. אנא נסה תמונה ברורה יותר.")
            
        return json.loads(safe_text)
        
    except json.JSONDecodeError:
        raise ValueError("שגיאה בפענוח הנתונים. ייתכן שהמסמך אינו קריא.")
    except Exception as e:
        # תופס שגיאות תקשורת, Timeout או Rate Limits מול השרתים של Groq
        raise RuntimeError(f"שירות ה-AI עמוס או אינו זמין כרגע. פרטים: {str(e)}")