import requests
import uuid

BASE_URL = "http://localhost:8000"

def run_tests():
    print("🚀 מתחיל בבדיקות אוטומטיות למערכת SmartStudent...\n")

    # נייצר שני משתמשים ייחודיים כדי לבדוק הרשאות
    user_a_email = f"alice_{uuid.uuid4().hex[:6]}@test.com"
    user_b_email = f"bob_{uuid.uuid4().hex[:6]}@test.com"
    password = "SecurePassword123"

    # --- טסט 1: הרשמה והתחברות ---
    print("🛠️ טסט 1: יצירת משתמשים והנפקת טוקנים...")
    
    # ניסיון הרשמה - משתמש א'
    res_reg_a = requests.post(f"{BASE_URL}/register", json={"email": user_a_email, "password": password})
    
    # ניסיון התחברות - משתמש א' (מעודכן ל-login)
    res_tok_a = requests.post(f"{BASE_URL}/login", data={"username": user_a_email, "password": password})
    token_a = res_tok_a.json().get("access_token") if res_tok_a.status_code == 200 else None

    # יצירת משתמש ב' והתחברות (מעודכן ל-login)
    requests.post(f"{BASE_URL}/register", json={"email": user_b_email, "password": password})
    res_tok_b = requests.post(f"{BASE_URL}/login", data={"username": user_b_email, "password": password})
    token_b = res_tok_b.json().get("access_token") if res_tok_b.status_code == 200 else None
    
    assert token_a and token_b, f"❌ שגיאה: הטוקנים לא נוצרו! סטטוס שרת: {res_tok_a.status_code}"
    print("✅ משתמשים נוצרו וטוקנים הונפקו בהצלחה.")

   # --- טסט 2: העלאת חומר (User A) ---
    print("🛠️ טסט 2: העלאת חומר לימוד על ידי משתמש א'...")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # הוספנו פה את uploader_name ואת contact_email שהיו חסרים!
    material_payload = {
        "institution": "אוניברסיטת בן גוריון", 
        "course_name": "מבני נתונים", 
        "topic": "עצים",
        "material_type": "סיכום", 
        "availability": "קובץ דיגיטלי להורדה בלבד", 
        "year": "2025", 
        "semester": "א", 
        "lecturer": "דנה", 
        "material_format": "PDF", 
        "file_path": "/dummy/path.pdf",
        "uploader_name": "אליס הבודקת",
        "contact_email": user_a_email
    }
    
    res_upload = requests.post(f"{BASE_URL}/materials", json=material_payload, headers=headers_a)
    assert res_upload.status_code == 200, f"❌ שגיאה בהעלאה: {res_upload.text}"
    print("✅ חומר הועלה ונשמר בהצלחה.")

    # --- התיקון: שולפים את ה-ID של החומר החדש מהשרת כדי להשתמש בו בטסטים הבאים ---
    materials = requests.get(f"{BASE_URL}/materials").json()
    material_id = materials[-1]["id"] 

    # --- טסט 3: פריצת הרשאות - מחיקה (User B מנסה למחוק ל-User A) ---

    # --- טסט 3: פריצת הרשאות - מחיקה (User B מנסה למחוק ל-User A) ---
    print("🛠️ טסט 3: בדיקת אבטחה - משתמש ב' מנסה למחוק את הקובץ של א'...")
    headers_b = {"Authorization": f"Bearer {token_b}"}
    res_hack_delete = requests.delete(f"{BASE_URL}/materials/{material_id}", headers=headers_b)
    
    assert res_hack_delete.status_code == 403, "❌ אבטחה פרוצה! משתמש ב' הצליח למחוק קובץ לא שלו."
    print("✅ אבטחה תקינה: השרת חסם את המחיקה והחזיר 403 (Not Authorized).")

    # --- טסט 4: פריצת הרשאות - עריקה (User B מנסה לערוך ל-User A) ---
    print("🛠️ טסט 4: בדיקת אבטחה - משתמש ב' מנסה לערוך את הקובץ של א'...")
    res_hack_edit = requests.put(f"{BASE_URL}/materials/{material_id}", json=material_payload, headers=headers_b)
    
    assert res_hack_edit.status_code == 403, "❌ אבטחה פרוצה! משתמש ב' הצליח לערוך קובץ לא שלו."
    print("✅ אבטחה תקינה: השרת חסם את העריכה והחזיר 403.")

    # --- טסט 5: עריכה חוקית (User A עורך את עצמו) ---
    print("🛠️ טסט 5: עריכה חוקית - משתמש א' משנה את נושא הקובץ שלו...")
    material_payload["topic"] = "גרפים (מעודכן)"
    res_legal_edit = requests.put(f"{BASE_URL}/materials/{material_id}", json=material_payload, headers=headers_a)
    
    assert res_legal_edit.status_code == 200, f"❌ עריקה חוקית נכשלה: {res_legal_edit.text}"
    print("✅ עריכה חוקית בוצעה בהצלחה.")

    # --- טסט 6: מחיקה חוקית (User A מוחק את עצמו) ---
    print("🛠️ טסט 6: מחיקה חוקית - משתמש א' מוחק את הקובץ שלו...")
    res_legal_delete = requests.delete(f"{BASE_URL}/materials/{material_id}", headers=headers_a)
    
    # הוספנו הדפסה כדי לראות מה השרת עונה לנו
    print(f"DEBUG Delete A: {res_legal_delete.status_code} - {res_legal_delete.text}")
    
    assert res_legal_delete.status_code == 200, f"❌ מחיקה חוקית נכשלה: {res_legal_delete.text}"
    print("✅ מחיקה חוקית בוצעה בהצלחה.")

    print("\n🎉🎉 כל בדיקות השרת (Backend) עברו בהצלחה! המערכת יציבה ומאובטחת. 🎉🎉")

if __name__ == "__main__":
    run_tests()