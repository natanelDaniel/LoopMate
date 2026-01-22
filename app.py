import streamlit as st
from supabase import create_client
from streamlit_calendar import calendar
from datetime import datetime, timedelta

# חיבור ל-Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

st.set_page_config(page_title="LoopMate Vietnam", page_icon="🏍️", layout="wide")

def update_and_get_visits():
    try:
        # עדכון המונה ב-1 (שורת ה-SQL שרצה בשרת)
        supabase.rpc('increment_visit_count').execute() # דורש פונקציית RPC ב-Supabase
        # או בדרך פשוטה יותר ללא RPC:
        res = supabase.table("site_stats").select("visit_count").eq("id", 1).execute()
        current_count = res.data[0]['visit_count']
        new_count = current_count + 1
        supabase.table("site_stats").update({"visit_count": new_count}).eq("id", 1).execute()
        return new_count
    except:
        return "---"

# הרצת המונה פעם אחת בכל טעינה של האתר
if 'counted' not in st.session_state:
    st.session_state.visit_total = update_and_get_visits()
    st.session_state.counted = True

# --- עיצוב CSS סקסי (ניקיון המונים ולוח השנה) ---
st.markdown("""
    <style>
    /* רקע האפליקציה */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #ffffff;
    }
    
    /* מונה לופים מרכזי */
    .total-counter {
        text-align: center;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(0, 210, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        max-width: 300px;
        margin: 0 auto 30px auto;
    }

    /* הפיכת לוח השנה לשקוף ומשתלב */
    .fc {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 10px;
    }

    /* תיקון צבעי טקסט בלוח שנה */
    .fc-theme-standard td, .fc-theme-standard th {
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .fc-col-header-cell-cushion, .fc-daygrid-day-number {
        color: rgba(255, 255, 255, 0.9) !important;
        text-decoration: none !important;
    }

    /* עיצוב כפתור הוספה */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        border: none;
        border-radius: 50px;
        color: white;
        font-weight: bold;
        padding: 15px 40px;
        font-size: 18px;
        transition: 0.3s ease;
        display: block;
        margin: 0 auto;
    }
    
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30)
def get_loop_data():
    res = supabase.table("loops").select("*").execute()
    return res.data

# שליפת נתונים
db_events = get_loop_data()
total_loops = len(db_events)

# --- תצוגת כותרת ומונה מרכזי ---
st.markdown("<h1 style='text-align: center; margin-bottom: 10px;'>LoopMate Vietnam 🇻🇳</h1>", unsafe_allow_html=True)

# מונה לופים מרכזי בודד
st.markdown(f"""
    <div class='total-counter'>
        <h2 style='margin:0; color:#00d2ff; font-size: 40px;'>{total_loops}</h2>
        <p style='margin:0; opacity:0.8; font-size: 16px;'>לופים שפורסמו עד כה</p>
    </div>
    """, unsafe_allow_html=True)

# --- לוגיקת תצוגה ---
if "show_form" not in st.session_state:
    st.session_state.show_form = False

if st.session_state.show_form:
    col_b1, col_b2, col_b3 = st.columns([1,1,1])
    with col_b2:
        if st.button("⬅️ חזרה ללוח השנה"):
            st.session_state.show_form = False
            st.rerun()
    
    with st.form("sexy_form"):
        st.markdown("### 🏍️ פרטי הלופ שלך")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("שם / כינוי")
            phone = st.text_input("מספר פלאפון (למשל 0501234567)")
            date = st.date_input("תאריך יציאה")
        with c2:
            duration = st.number_input("כמה ימים הלופ?", min_value=1, value=3)
            size = st.number_input("כמה אנשים אתם?", min_value=1, value=1)
            delete_code = st.text_input("קוד אישי למחיקה", type="password")
        
        notes = st.text_area("הערות (נהגים, סגנון רכיבה וכו')")
        
        if st.form_submit_button("פרסם לופ! 🚀"):
            if name and phone and delete_code:
                clean_phone = phone.replace("-", "").replace(" ", "").replace("+", "")
                if clean_phone.startswith("0"): clean_phone = "972" + clean_phone[1:]
                data = {
                    "name": name, "start_date": str(date), "duration_days": duration,
                    "group_size": size, "phone": phone, "whatsapp_link": f"https://wa.me/{clean_phone}",
                    "delete_code": delete_code, "notes": notes
                }
                supabase.table("loops").insert(data).execute()
                st.cache_data.clear()
                st.session_state.show_form = False
                st.rerun()
else:
    # כפתור הוספה מרכזי
    if st.button("➕ הוסף את הלופ שלי"):
        st.session_state.show_form = True
        st.rerun()

    # הכנת אירועים ללוח
    calendar_events = []
    for ev in db_events:
        start = datetime.strptime(ev['start_date'], "%Y-%m-%d")
        end = start + timedelta(days=ev['duration_days'])
        calendar_events.append({
            "title": f"🏍️ {ev['name']} ({ev['group_size']})",
            "start": ev['start_date'],
            "end": end.strftime("%Y-%m-%d"),
            "backgroundColor": "#3498db",
            "extendedProps": {"wa_url": ev['whatsapp_link']}
        })

    calendar_options = {
        "initialView": "dayGridMonth",
        "direction": "ltr",
        "firstDay": 0,
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,dayGridWeek"}
    }

    state = calendar(events=calendar_events, options=calendar_options, key="sexy_calendar")

    if state.get("eventClick"):
        wa_url = state["eventClick"]["event"]["extendedProps"]["wa_url"]
        st.components.v1.html(f"<script>window.open('{wa_url}', '_blank');</script>", height=0)

    # אזור מחיקה
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🗑️ למחיקת הפרסום שלך"):
        m_col1, m_col2, m_col3 = st.columns([2,2,1])
        with m_col1:
            names = [ev['name'] for ev in db_events]
            name_to_del = st.selectbox("בחר שם", names) if names else st.selectbox("בחר שם", ["אין לופים"])
        with m_col2:
            del_code = st.text_input("קוד אישי", type="password", key="del_pwd")
        with m_col3:
            st.write(" ")
            if st.button("מחק"):
                target = next((item for item in db_events if item["name"] == name_to_del), None)
                if target and del_code == target['delete_code']:
                    supabase.table("loops").delete().eq("id", target['id']).execute()
                    st.cache_data.clear()
                    st.rerun()
# --- הצגת מונה הכניסות בתחתית העמוד ---
st.markdown(f"<div class='footer-counter'>סה\"כ כניסות לאתר: {st.session_state.visit_total}</div>", unsafe_allow_html=True)
