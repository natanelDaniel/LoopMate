import streamlit as st
from supabase import create_client
from streamlit_calendar import calendar
from datetime import datetime, timedelta

# חיבור ל-Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

st.set_page_config(page_title="LoopMate Vietnam", page_icon="🏍️", layout="wide")

# --- מנגנון מונה כניסות (Analytics פשוט) ---
if 'visits' not in st.session_state:
    # כאן אנחנו משתמשים ב-Session State כדי לספור כניסות באותו סשן
    # כדי לספור כניסות גלובליות לאורך זמן, מומלץ לשמור טבלה ייעודית ב-Supabase
    st.session_state.visits = True
    try:
        # עדכון מונה גלובלי ב-Supabase (מניח שיש טבלה בשם 'analytics')
        supabase.rpc('increment_visit_count', {}).execute()
    except:
        pass

# --- עיצוב CSS סקסי ומתקדם ---
st.markdown("""
    <style>
    /* רקע האפליקציה עם גרדיאנט עמוק */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #ffffff;
    }
    
    /* הפיכת לוח השנה ל"שקוף" וסקסי באמת */
    .fc {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 15px;
    }

    /* תיקון צבעי הטקסט בלוח שהיו שחורים */
    .fc-theme-standard td, .fc-theme-standard th {
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    .fc-col-header-cell-cushion, .fc-daygrid-day-number {
        color: rgba(255, 255, 255, 0.85) !important;
        text-decoration: none !important;
    }

    .fc-toolbar-title {
        color: #00d2ff !important;
        font-weight: 800 !important;
        text-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
    }

    /* עיצוב כרטיסיות המונים */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(0, 210, 255, 0.2);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    /* עיצוב כפתור הוספה */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        border: none;
        border-radius: 50px;
        color: white;
        font-weight: bold;
        padding: 12px 25px;
        transition: 0.3s;
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

# --- תצוגת כותרת ומונים ---
st.markdown("<h1 style='text-align: center;'>LoopMate Vietnam</h1>", unsafe_allow_html=True)

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.markdown(f"<div class='metric-card'><h3 style='margin:0; color:#00d2ff;'>{total_loops}</h3><p style='margin:0; opacity:0.7;'>לופים שפורסמו</p></div>", unsafe_allow_html=True)
with col_m2:
    # כאן נדרשת טבלה ב-Supabase כדי להציג מונה אמיתי
    st.markdown(f"<div class='metric-card'><h3 style='margin:0; color:#43e97b;'>LIVE</h3><p style='margin:0; opacity:0.7;'>מערכת פעילה</p></div>", unsafe_allow_html=True)
with col_m3:
    st.markdown(f"<div class='metric-card'><h3 style='margin:0; color:#fa709a;'>24/7</h3><p style='margin:0; opacity:0.7;'>זמינות מלאה</p></div>", unsafe_allow_html=True)

st.write("---")

# --- לוגיקת תצוגת טופס/לוח ---
if "show_form" not in st.session_state:
    st.session_state.show_form = False

if st.session_state.show_form:
    if st.button("⬅️ חזרה ללוח השנה"):
        st.session_state.show_form = False
        st.rerun()
    
    with st.form("sexy_form"):
        # (כאן הקוד של הטופס שהיה לנו קודם - נשאר אותו דבר)
        st.markdown("### פרטי הלופ החדש")
        # ... (שאר שדות הטופס)
        if st.form_submit_button("LFG! 🚀"):
            # ... (לוגיקת שמירה ל-Supabase)
            st.rerun()
else:
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
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

    # הגדרות לוח שנה
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
