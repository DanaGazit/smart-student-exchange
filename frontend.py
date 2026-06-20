import streamlit as st
import requests
import urllib.parse
import os
import re
import datetime

# --- Configuration & API Functions ---
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")

def register_user(email, password):
    try:
        return requests.post(f"{BACKEND_URL}/register", json={"email": email, "password": password})
    except requests.exceptions.ConnectionError:
        return None

def login_user(email, password):
    try:
        return requests.post(f"{BACKEND_URL}/login", data={"username": email, "password": password})
    except requests.exceptions.ConnectionError:
        return None

# --- Application Configuration ---
st.set_page_config(page_title="Smart Student Exchange", page_icon="🎓", layout="centered")

# --- UI Styling (CSS) ---
st.markdown("""
    <style>
    .stApp { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; }
    [data-testid="stSidebar"] { direction: rtl; }
    p, div, input, label, h2, h3 { text-align: right; }
    
    .title-wrapper { display: flex; justify-content: center; margin-top: 20px; margin-bottom: 20px; }
    .title-bubble {
        background: linear-gradient(135deg, #0A2342, #17408B);
        padding: 15px 40px;
        border-radius: 50px;
        box-shadow: 0 10px 25px rgba(10, 35, 66, 0.4);
        display: inline-block;
    }
    .title-bubble h1 { color: white !important; font-size: 3rem; font-weight: 900; margin: 0; text-align: center !important; letter-spacing: 1px; }
    
    .select-title { text-align: center !important; font-size: 1.6rem; font-weight: 800; color: #182848; margin-bottom: 10px; margin-top: 10px; }
    
    .vision-box {
        background-color: white; padding: 35px; border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06); border-top: 4px solid #17408B;
        margin-bottom: 40px; margin-top: 40px;
    }
    .vision-box h3 { text-align: center !important; color: #182848; margin-bottom: 20px; font-weight: 800; }
    .vision-box p { text-align: center !important; font-size: 1.15rem; color: #444; line-height: 1.8; }
    .highlight-pay { font-weight: 900; color: #17408B; font-size: 1.4rem; display: inline-block; }

    .stButton>button { border-radius: 8px; font-weight: bold; font-size: 1.1rem !important; padding: 10px !important; transition: all 0.3s ease; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(23, 64, 139, 0.2); }
    </style>
""", unsafe_allow_html=True)

# --- 1. State Management (חייב להיות בראש הקוד!) ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_institution' not in st.session_state:
    st.session_state.selected_institution = "אוניברסיטת בן גוריון"
if 'ai_data' not in st.session_state:
    st.session_state.ai_data = None
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "registration_success" not in st.session_state:
    st.session_state.registration_success = False
if "editing_material_id" not in st.session_state:
    st.session_state.editing_material_id = None    

# --- פונקציות ניווט (הגדרנו אותן כאן כדי למנוע NameError) ---
def go_to_hub(institution):
    st.session_state.selected_institution = institution
    st.session_state.page = 'hub'

def go_to_home():
    st.session_state.page = 'home'
    st.session_state.ai_data = None

# --- 2. Top Navigation Bar (Header) ---
col_empty, col_logo, col_auth = st.columns([1, 3, 1.5])

with col_auth:
    display_name = st.session_state.user_email.split('@')[0] if st.session_state.user_email else "איזור אישי"
    auth_popover = st.popover(f"👤 {display_name}", use_container_width=True)
    
    with auth_popover:
        if st.session_state.token is None:
            mode = st.radio("פעולה:", ["התחברות", "הרשמה"], horizontal=True)
            
            email_in = st.text_input("אימייל", placeholder="example@mail.com", autocomplete="email", key="email_field")
            pass_in = st.text_input("סיסמה", type="password", placeholder="******", autocomplete="new-password", key="pass_field")
            
            if mode == "הרשמה":
                if st.button("צור חשבון", type="primary", use_container_width=True):
                    # --- תוספת: ולידציה של מייל וסיסמה ---
                    if not email_in or not pass_in:
                        st.warning("נא למלא את כל השדות")
                    elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email_in):
                        st.error("כתובת המייל אינה תקינה ❌")
                    elif len(pass_in) < 6 or re.search(r'[\u0590-\u05FF]', pass_in):
                        st.error("הסיסמה חייבת להכיל לפחות 6 תווים ורק אותיות באנגלית/מספרים 🔒")
                    else:
                        reg_res = register_user(email_in, pass_in)
                        
                        if reg_res is not None:
                            if reg_res.status_code == 200:
                                log_res = login_user(email_in, pass_in)
                                if log_res and log_res.status_code == 200:
                                    token_data = log_res.json()
                                    st.session_state.token = token_data["access_token"]
                                    st.session_state.user_email = email_in
                                    st.success("נרשמת וחוברת בהצלחה! 🎉")
                                    st.rerun()
                            elif reg_res.status_code == 400:
                                error_msg = reg_res.json().get('detail', 'המייל הזה כבר רשום במערכת')
                                st.warning(f"⚠️ {error_msg}")
                            else:
                                st.error(f"שגיאת שרת כללית: {reg_res.status_code}")
                        else:
                            st.error("השרת לא מגיב. ודא שה-Backend רץ 🔌")
            elif mode == "התחברות":
                if st.button("התחבר", type="primary", use_container_width=True):
                    if not email_in or not pass_in:
                        st.warning("נא להזין מייל וסיסמה")
                    else:
                        log_res = login_user(email_in, pass_in)
                        
                        if log_res is not None:
                            if log_res.status_code == 200:
                                token_data = log_res.json()
                                st.session_state.token = token_data["access_token"]
                                st.session_state.user_email = email_in
                                st.rerun()
                            elif log_res.status_code in [400, 401]:
                                error_msg = log_res.json().get('detail', 'פרטי התחברות שגויים')
                                st.error(f"שגיאת התחברות: {error_msg} ❌")
                            else:
                                st.error(f"שגיאת שרת כללית: {log_res.status_code}")
                        else:
                            st.error("השרת לא מגיב. ודא שה-Backend רץ 🔌")
        else:
            # תצוגה למשתמש מחובר (RTL Fix)
            st.markdown(f"""
                <div style="text-align: right; direction: rtl; margin-bottom: 15px;">
                    מחובר כ: <br>
                    <span style="direction: ltr; unicode-bidi: embed; font-weight: bold; color: #17408B;">
                        {st.session_state.user_email}
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("התנתק", use_container_width=True):
                st.session_state.token = None
                st.session_state.user_email = None
                st.rerun()

# ==========================================
# View: Home Page
# ==========================================
if st.session_state.page == 'home':
    st.markdown("""
        <div class="title-wrapper">
            <div class="title-bubble">
                <h1>Smart Student Exchange</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="select-title">🏫 באיזה מוסד אקדמי אתם לומדים?</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        institutions = ["אוניברסיטת בן גוריון", "אוניברסיטת תל אביב", "האוניברסיטה העברית", "הטכניון", "אוניברסיטת בר אילן", "אחר"]
        default_idx = institutions.index(st.session_state.selected_institution) if st.session_state.selected_institution in institutions else 0
        selected_inst = st.selectbox("בחר מוסד", institutions, index=default_idx, label_visibility="collapsed")
        
        st.write("")
        if st.button("🚀 כניסה לספרייה", type="primary", use_container_width=True):
            go_to_hub(selected_inst)
            st.rerun()

    st.markdown("""
        <div class="vision-box">
            <h3>החזון שלנו 🎯</h3>
            <p>
            יש לכם סיכומים מודפסים שסתם שוכבים בבית? עבדתם שעות על סיכום או דף נוסחאות מושקע? <br>
            <span dir="ltr" class="highlight-pay">PAY IT FORWARD!</span><br><br>
            במקום לזרוק אותם לפח בתום הסמסטר, המערכת שלנו מאפשרת לכם להעביר, להשאיל או לשתף חומרי לימוד פיזיים ודיגיטליים בקלות עם סטודנטים שצריכים אותם עכשיו.<br>
            החלק הכי טוב? אתם אפילו לא צריכים להקליד כלום. פשוט צלמו את המסמך, ותנו לבינה המלאכותית לעשות את כל עבודת הקיטלוג השחורה עבורכם.
            </p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# View: Institution Hub (Upload & Library)
# ==========================================
elif st.session_state.page == 'hub':
    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.header(f"🎓 המרכז של {st.session_state.selected_institution}")
    with header_col2:
        if st.button("🔙 שינוי מוסד"):
            go_to_home()
            st.rerun()
            
    st.divider()
    
    tab_upload, tab_library = st.tabs(["📤 שיתוף חומר חדש", "🔍 חיפוש בספרייה"])
    
    with tab_upload:
        if st.session_state.token is None:
            st.warning("🔒 כדי להעלות חומרים חדשים, עליך להתחבר למערכת ")
        else:
            st.subheader("העלו תמונה או קובץ (PDF), ותנו ל-AI לנתח אותו בשבילכם⚡")
            uploaded_file = st.file_uploader("בחר קובץ (תמונה או PDF)", type=["jpg", "png", "jpeg", "pdf"])
            if uploaded_file is not None:
                if uploaded_file.type == "application/pdf" or uploaded_file.name.lower().endswith('.pdf'):
                    st.info(f"📄 קובץ PDF נטען בהצלחה: {uploaded_file.name}")
                else:
                    st.image(uploaded_file, caption="החומר שהועלה", width=300)
                
                if st.button("🤖 נתח מסמך"):
                    with st.spinner("ה-AI קורא את המסמך..."):
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        try:
                            response = requests.post(f"{BACKEND_URL}/analyze-material", files=files)
                            if response.status_code == 200:
                                result = response.json()
                                if "data" in result:
                                    st.session_state.ai_data = result["data"]
                                    st.rerun()
                                else:
                                    st.error(f"שגיאת שרת: {result.get('error', 'לא ידוע')}")
                            else:
                                st.error("שגיאת תקשורת מול השרת.")
                        except requests.exceptions.ConnectionError:
                            st.error("השרת מכובה! נא להדליק את ה-Backend.")

            if st.session_state.ai_data:
                st.success("הפענוח הושלם! אנא ודא שהפרטים נכונים ותקן במידת הצורך:")
                data = st.session_state.ai_data
                
                with st.container(border=True):
                    course_name = st.text_input("📚 שם הקורס (חובה):", value=data.get("course_name", ""))
                    topic = st.text_input("📝 נושא (חובה):", value=data.get("topic", ""))
                    
                    options = ["סיכום", "מבחן", "שיעורי בית", "דף נוסחאות"]
                    default_index = options.index(data.get("material_type")) if data.get("material_type") in options else 0
                    material_type = st.selectbox("📂 סוג החומר (חובה):", options, index=default_index)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        year = st.text_input("📅 שנה:", value=data.get("year", "לא צוין"))
                    with col2:
                        semester_options = ["סמסטר א", "סמסטר ב", "לא צוין"]
                        ai_semester = data.get("semester", "לא צוין")
                        if ai_semester == "א": ai_semester = "סמסטר א"
                        elif ai_semester == "ב": ai_semester = "סמסטר ב"
                        default_sem_index = semester_options.index(ai_semester) if ai_semester in semester_options else 2
                        semester = st.selectbox("⏳ סמסטר:", semester_options, index=default_sem_index)
                        
                    col3, col4 = st.columns(2)
                    with col3:
                        lecturer = st.text_input("👨‍🏫 שם המרצה (רשות):", value=data.get("lecturer", ""))
                    with col4:
                        format_options = ["מודפס", "בכתב יד", "דיגיטלי (קובץ בלבד)", "לא ידוע"]
                        ai_format = data.get("material_format", "לא ידוע")
                        default_fmt_index = format_options.index(ai_format) if ai_format in format_options else 3
                        material_format = st.selectbox("🖨️ פורמט החומר (רשות):", format_options, index=default_fmt_index)
                
                    uploader_name = st.text_input("👤 שם הסטודנט/ית המעלה (רשות):", value=st.session_state.user_email)
                    
                    st.markdown("### 📦 אופן המסירה")
                    
                    avail_options = ["זמין למסירה פיזית", "קובץ דיגיטלי להורדה בלבד", "מושאל (עד תאריך מסוים)", "לא זמין כרגע"]
                    new_avail_base = st.selectbox("זמינות החומר הפיזי", avail_options)
                    
                    # הצגת שדה תאריך דינמי אם נבחרה השאלה
                    selected_date = datetime.date.today()
                    if new_avail_base == "מושאל (עד תאריך מסוים)":
                        selected_date = st.date_input("תאריך חזרה משוער:", value=selected_date)

                    is_physical_delivery = new_avail_base in ["זמין למסירה פיזית", "מושאל (עד תאריך מסוים)"]
                    email_label = "מייל ליצירת קשר (חובה למסירה פיזית)" if is_physical_delivery else "מייל ליצירת קשר (רשות)"
                    contact_email = st.text_input(email_label, value=st.session_state.user_email)
                    
                    if st.button("✅ אשר ושמור במערכת", type="primary", use_container_width=True):
                        safe_email = contact_email if contact_email else ""
                        
                        if is_physical_delivery and safe_email.strip() == "":
                            st.error("אנא הזן כתובת מייל לתיאום איסוף.")
                        else:
                            # 1. הרכבת הסטטוס הסופי לפני שליחה ל-DB
                            final_val = f"בהשאלה עד: {selected_date}" if new_avail_base == "מושאל (עד תאריך מסוים)" else new_avail_base
                            
                            # 2. הרכבת ה-Payload (החלפנו את availability ב-final_val)
                            payload = {
                                "institution": st.session_state.selected_institution,
                                "course_name": course_name, 
                                "topic": topic,
                                "material_type": material_type, 
                                "uploader_name": uploader_name,
                                "contact_email": contact_email, 
                                "availability": final_val, 
                                "year": year, 
                                "semester": semester, 
                                "lecturer": lecturer,
                                "material_format": material_format,
                                "file_path": st.session_state.ai_data.get("file_path", "")
                            }
                            headers = {"Authorization": f"Bearer {st.session_state.token}"}
                            
                            try:
                                save_response = requests.post(f"{BACKEND_URL}/materials", json=payload, headers=headers)
                                if save_response.status_code == 200:
                                    st.success("החומר נשמר בהצלחה! תוכל למצוא אותו בספרייה.")
                                    st.session_state.ai_data = None
                                    st.rerun()
                                elif save_response.status_code == 401:
                                    st.error("החיבור פג תוקף, אנא התחבר מחדש.")
                                else:
                                    st.error(f"שגיאה בשמירת הנתונים: {save_response.text}")
                            except Exception as e:
                                st.error("שגיאה בתקשורת מול השרת.")
                        
    with tab_library:
            try:
                response = requests.get(f"{BACKEND_URL}/materials")
                if response.status_code == 200:
                    all_materials = response.json()
                    relevant_materials = [mat for mat in all_materials if mat.get("institution") == st.session_state.selected_institution]
                    
                    if not relevant_materials:
                        st.info("עדיין אין חומרים עבור המוסד הזה.")
                    else:
                        search_query = st.text_input("🔍 חיפוש קורס או נושא:", placeholder="לדוגמה: מבנה נתונים...")
                        for mat in relevant_materials:
                            if not search_query or search_query.lower() in mat.get("course_name", "").lower() or search_query.lower() in mat.get("topic", "").lower():
                                with st.expander(f"📖 {mat['course_name']} - {mat['topic']} ({mat['material_type']})"):
                                    st.write(f"**הועלה על ידי:** {mat.get('uploader_name', 'אנונימי')}")
                                    st.write(f"**זמינות:** {mat.get('availability', 'לא צוין')}")
                                    
                                    if mat.get('file_path'):
                                        public_backend_url = BACKEND_URL.replace("backend", "localhost")
                                        file_url = f"{public_backend_url}{mat['file_path']}"
                                        st.link_button("📥 צפה בסריקה", file_url, use_container_width=True)

                                    # --- לוגיקת כלי ניהול ---
                                    current_user_email = str(st.session_state.get("user_email", "")).strip().lower()
                                    material_owner_email = str(mat.get('user_id', '')).strip().lower()
                                    is_owner = bool(st.session_state.get("token")) and (current_user_email == material_owner_email)

                                    if is_owner:
                                        st.markdown("---")
                                        
                                        # בדיקה: האם הקובץ הנוכחי נמצא במצב עריכה?
                                        if st.session_state.editing_material_id == mat['id']:
                                            st.info("✏️ עריכת פרטי קובץ")
                                            
                                            # --- ניהול זמינות מחוץ לטופס כדי לאפשר רענון דינמי של התאריך ---
                                            current_avail = mat.get('availability', '')
                                            avail_options = ["זמין למסירה פיזית", "קובץ דיגיטלי להורדה בלבד", "מושאל (עד תאריך מסוים)", "לא זמין כרגע"]
                                            
                                            is_borrowed_now = "בהשאלה עד:" in current_avail
                                            idx = 2 if is_borrowed_now else (avail_options.index(current_avail) if current_avail in avail_options else 0)
                                            
                                            # השדה הזה יגרום לרענון הדף ברגע שמשנים אותו (כי הוא מחוץ ל-form)
                                            new_avail_base = st.selectbox("סטטוס זמינות", avail_options, index=idx, key=f"select_avail_{mat['id']}")

                                            # הצגת שדה תאריך רק אם נבחר "מושאל"
                                            selected_date = datetime.date.today()
                                            if new_avail_base == "מושאל (עד תאריך מסוים)":
                                                if is_borrowed_now:
                                                    try:
                                                        date_str = current_avail.split(": ")[1].strip()
                                                        selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                                                    except: pass
                                                selected_date = st.date_input("עד איזה תאריך?", value=selected_date, key=f"date_{mat['id']}")

                                            # שאר השדות בתוך טופס כדי לשמור על סדר בשליחה
                                            with st.form(key=f"form_full_edit_{mat['id']}"):
                                                col1, col2 = st.columns(2)
                                                with col1:
                                                    new_course = st.text_input("שם הקורס", value=mat.get('course_name', ''))
                                                    new_institution = st.text_input("מוסד לימודים", value=mat.get('institution', ''))
                                                    new_year = st.text_input("שנה", value=mat.get('year', ''))
                                                    new_format = st.text_input("פורמט", value=mat.get('material_format', ''))
                                                with col2:
                                                    new_topic = st.text_input("נושא", value=mat.get('topic', ''))
                                                    new_lecturer = st.text_input("מרצה", value=mat.get('lecturer', ''))
                                                    new_semester = st.text_input("סמסטר", value=mat.get('semester', ''))
                                                    new_type = st.text_input("סוג החומר", value=mat.get('material_type', ''))

                                                if st.form_submit_button("💾 שמור שינויים", type="primary", use_container_width=True):
                                                    # הרכבת הסטטוס הסופי
                                                    final_val = f"בהשאלה עד: {selected_date}" if new_avail_base == "מושאל (עד תאריך מסוים)" else new_avail_base
                                                    
                                                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                                                    payload = {
                                                        "institution": new_institution, "course_name": new_course, "topic": new_topic,
                                                        "material_type": new_type, "availability": final_val, "year": new_year,
                                                        "semester": new_semester, "lecturer": new_lecturer, "material_format": new_format
                                                    }
                                                    
                                                    res = requests.put(f"{BACKEND_URL}/materials/{mat['id']}", json=payload, headers=headers)
                                                    if res.status_code == 200:
                                                        st.success("הנתונים עודכנו בהצלחה!")
                                                        st.session_state.editing_material_id = None
                                                        st.rerun()
                                                    else:
                                                        st.error(f"שגיאת שרת: {res.text}")

                                                if st.form_submit_button("❌ ביטול", use_container_width=True):
                                                    st.session_state.editing_material_id = None
                                                    st.rerun()

                                        else:
                                            st.caption("🛠️ כלי ניהול")
                                            c1, c2 = st.columns(2)
                                            with c1:
                                                if st.button("✏️ ערוך", key=f"btn_ed_{mat['id']}", use_container_width=True):
                                                    st.session_state.editing_material_id = mat['id']
                                                    st.rerun()
                                            with c2:
                                                if st.button("🗑️ מחק", key=f"btn_del_{mat['id']}", use_container_width=True):
                                                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                                                    res = requests.delete(f"{BACKEND_URL}/materials/{mat['id']}", headers=headers)
                                                    if res.status_code == 200:
                                                        st.success("נמחק בהצלחה")
                                                        st.rerun()
            except Exception as e:
                st.warning("השרת כבוי או שיש בעיית תקשורת.")