import streamlit as st
import requests
import urllib.parse

# --- Application Configuration ---
st.set_page_config(page_title="Smart Student Exchange", page_icon="🎓", layout="centered")

# --- UI Styling (CSS) ---
st.markdown("""
    <style>
    .stApp { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; }
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
    
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent; border-radius: 4px 4px 0px 0px; padding-top: 10px; padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- State Management (Routing) ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_institution' not in st.session_state:
    st.session_state.selected_institution = "אוניברסיטת בן גוריון"
if 'ai_data' not in st.session_state:
    st.session_state.ai_data = None

def go_to_hub(institution):
    st.session_state.selected_institution = institution
    st.session_state.page = 'hub'

def go_to_home():
    st.session_state.page = 'home'
    st.session_state.ai_data = None

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
    
    st.markdown('<div class="select-title"> באיזה מוסד אקדמי אתם לומדים? 🏫</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        institutions = ["אוניברסיטת בן גוריון", "אוניברסיטת תל אביב", "האוניברסיטה העברית", "הטכניון", "אוניברסיטת בר אילן", "אחר"]
        default_idx = institutions.index(st.session_state.selected_institution) if st.session_state.selected_institution in institutions else 0
        selected_inst = st.selectbox("בחר מוסד", institutions, index=default_idx, label_visibility="collapsed")
        
        st.write("")
        if st.button("כניסה לספרייה 🚀", type="primary", use_container_width=True):
            go_to_hub(selected_inst)
            st.rerun()

    st.markdown("""
        <div class="vision-box">
            <h3>החזון שלנו 🎯</h3>
            <p>
            יש לכם סיכומים מודפסים שסתם שוכבים בבית? עבדתם שעות על סיכום או דף נוסחאות מושקע? <br>
            <span dir="ltr" class="highlight-pay">PAY IT FORWARD!</span><br><br>
            במקום לזרוק אותם לפח בתום הסמסטר, המערכת שלנו מאפשרת לכם להעביר, להשאיל או לשתף חומרי לימוד פיזיים ודיגיטליים בקלות עם סטודנטים שצריכים אותם עכשיו.<br>
            החלק הכי טוב? אתם אפילו לא צריכים להקליד כלום. פשוט העלו את המסמך, ותנו לבינה המלאכותית (AI) שלנו לעשות את כל עבודת הקיטלוג השחורה עבורכם.
            </p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# View: Institution Hub (Upload & Library)
# ==========================================
elif st.session_state.page == 'hub':
    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.header(f"המרכז של {st.session_state.selected_institution} 🎓")
    with header_col2:
        if st.button("🔙 שינוי מוסד"):
            go_to_home()
            st.rerun()
            
    st.divider()
    
    tab_upload, tab_library = st.tabs(["📤 שיתוף חומר חדש", "🔍 חיפוש בספרייה"])
    
    # --- Tab 1: AI-Powered Upload ---
    with tab_upload:
        st.subheader("העלו תמונה או קובץ, ותנו ל-AI לנתח אותו בשבילכם ⚡")
        uploaded_file = st.file_uploader("בחר קובץ (תמונה או PDF)", type=["jpg", "png", "jpeg", "pdf"])

        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                st.info(f"📄 קובץ PDF הועלה בהצלחה!")
            else:
                st.image(uploaded_file, caption="החומר שהועלה", width=300)
            
            if st.button("🤖 נתח מסמך"):
                with st.spinner("ה-AI קורא את המסמך..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    try:
                        response = requests.post("http://backend:8000/analyze-material", files=files)
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

        # Render form after AI analysis
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
            
                uploader_name = st.text_input("👤 שם הסטודנט/ית המעלה (רשות):", value="אנונימי")
                
                st.markdown("### 📦 אופן המסירה")
                availability = st.selectbox("זמינות החומר הפיזי", ["למסירה לתמיד", "להשאלה (יש להחזיר)", "קובץ דיגיטלי להורדה בלבד"])
                
                is_physical_delivery = availability in ["למסירה לתמיד", "להשאלה (יש להחזיר)"]
                email_label = "מייל ליצירת קשר (חובה למסירה פיזית)" if is_physical_delivery else "מייל ליצירת קשר (רשות)"
                contact_email = st.text_input(email_label, placeholder="student@post.bgu.ac.il")
                
                st.write("")
                if st.button("✅ אשר ושמור במערכת", type="primary", use_container_width=True):
                    if is_physical_delivery and contact_email.strip() == "":
                        st.error("אנא הזן כתובת מייל כדי שסטודנטים יוכלו לתאם איתך את איסוף החומר הפיזי.")
                    elif contact_email.strip() != "" and ("@" not in contact_email or "." not in contact_email):
                        st.error("כתובת המייל שהוזנה אינה תקינה.")
                    else:
                        payload = {
                            "institution": st.session_state.selected_institution,
                            "course_name": course_name,
                            "topic": topic,
                            "material_type": material_type,
                            "uploader_name": uploader_name,
                            "contact_email": contact_email, 
                            "availability": availability,
                            "year": year,
                            "semester": semester,
                            "lecturer": lecturer,
                            "material_format": material_format,
                            "file_path": st.session_state.ai_data.get("file_path", "")
                        }    
                        
                        try:
                            save_response = requests.post("http://backend:8000/materials", json=payload)
                            if save_response.status_code == 200:
                                st.success("החומר נשמר בהצלחה! תוכל למצוא אותו בספרייה.")
                                st.session_state.ai_data = None
                            else:
                                st.error(f"שגיאה בשמירת הנתונים: {save_response.text}")
                        except Exception as e:
                            st.error("שגיאה בתקשורת מול השרת.")

    # --- Tab 2: Material Library & Search ---
    with tab_library:
        try:
            response = requests.get("http://backend:8000/materials")
            
            if response.status_code == 200:
                all_materials = response.json()
                relevant_materials = [mat for mat in all_materials if mat.get("institution") == st.session_state.selected_institution]
                
                if not relevant_materials:
                    st.info("עדיין אין חומרים עבור המוסד הזה. תהיו הראשונים לשתף בטאב 'העלאה'!")
                else:
                    # Search and Filtering Logic
                    filter_col1, filter_col2 = st.columns([2, 1])
                    
                    with filter_col1:
                        search_query = st.text_input("🔍 חיפוש קורס או נושא:", placeholder="לדוגמה: מבוא ל-DevOps או מבנה נתונים...")
                        
                    with filter_col2:
                        available_types = list(set([mat.get("material_type") for mat in relevant_materials if mat.get("material_type")]))
                        selected_types = st.multiselect("סוג חומר:", options=available_types, default=available_types)
                    
                    filtered_materials = []
                    for mat in relevant_materials:
                        search_match = search_query.lower() in mat.get("course_name", "").lower() or search_query.lower() in mat.get("topic", "").lower() if search_query else True
                        type_match = mat.get("material_type") in selected_types
                        if search_match and type_match:
                            filtered_materials.append(mat)
                    
                    st.write(f"מציג **{len(filtered_materials)}** מתוך **{len(relevant_materials)}** חומרים במוסד:")
                    
                    # Display Results
                    for mat in filtered_materials:
                        with st.expander(f"📖 {mat['course_name']} - {mat['topic']} ({mat['material_type']})"):
                            info_col1, info_col2 = st.columns(2)
                            with info_col1:
                                st.write(f"**שנה וסמסטר:** {mat.get('year', 'לא צוין')} | {mat.get('semester', 'לא צוין')}")
                                if mat.get('lecturer'):
                                    st.write(f"**מרצה:** {mat['lecturer']}")
                            
                            with info_col2:
                                if mat.get('material_format'):
                                    st.write(f"**פורמט:** {mat['material_format']}")
                                st.write(f"**זמינות:** {mat.get('availability', 'לא צוין')}")
                                st.write(f"**הועלה על ידי:** {mat.get('uploader_name', 'אנונימי')}")
                            
                            action_col1, action_col2 = st.columns(2)
                            
                            with action_col1:
                                is_physical = mat.get('availability') in ["למסירה לתמיד", "להשאלה (יש להחזיר)"]
                                if mat.get('contact_email') and is_physical:
                                    subject = f"בקשה בנוגע לחומר: {mat['course_name']} - {mat['topic']}"
                                    body = f"היי {mat.get('uploader_name', '')},\nראיתי שהעלית את החומר '{mat['topic']}' בקורס {mat['course_name']}.\nאשמח לתאם איתך מתי אפשר לאסוף אותו!\n\nתודה רבה,"
                                    safe_subject = urllib.parse.quote(subject)
                                    safe_body = urllib.parse.quote(body)
                                    gmail_link = f"[https://mail.google.com/mail/?view=cm&fs=1&to=](https://mail.google.com/mail/?view=cm&fs=1&to=){mat['contact_email']}&su={safe_subject}&body={safe_body}"
                                    st.link_button("✉️ תיאום מסירה (Gmail)", gmail_link, use_container_width=True)
                                elif not is_physical:
                                    st.button("✉️ פיזי לא זמין", disabled=True, key=f"no_mail_{mat.get('id', mat['topic'])}", use_container_width=True)
                            
                            with action_col2:
                                if mat.get('file_path'):
                                    file_url = f"http://backend:8000{mat['file_path']}"
                                    try:
                                        res = requests.get(file_url)
                                        if res.status_code == 200:
                                            st.download_button(
                                                label="📥 הורד סריקה",
                                                data=res.content,
                                                file_name=mat['file_path'].split('/')[-1],
                                                key=f"dl_{mat.get('id', mat['topic'])}",
                                                use_container_width=True
                                            )
                                    except Exception as e:
                                        pass
                                        
        except requests.exceptions.ConnectionError:
            st.warning("השרת כבוי, לא ניתן להציג את הספרייה.")