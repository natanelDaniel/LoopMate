import streamlit as st
from supabase import create_client
from streamlit_calendar import calendar
from datetime import datetime, timedelta

# חיבור ל-Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

st.set_page_config(page_title="LoopMate Vietnam", page_icon="🏍️", layout="wide")

# --- עיצוב CSS סקסי (שקיפות וניאון) ---
st.markdown("""
    <style>
    /* רקע האפליקציה הכללי */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    
    /* הפיכת הלוח לשקוף ומעוצב */
    .fc {
        background: transparent !important; /* ביטול הרקע השחור */
        border: none !important;
        color: white !important;
    }

    /* עיצוב התאים (הריבועים) של הלוח */
    .fc-daygrid-day {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* כותרות ימי השבוע */
    .fc-col-header-cell-cushion {
        color: #3498db !important;
        font-weight: bold;
        text-transform: uppercase;
    }

    /* מספרי הימים */
    .fc-daygrid-day-number {
        color: rgba(255, 255, 255, 0.6) !important;
        padding: 5px !important;
    }

    /* הדגשת היום הנוכחי */
    .fc-day-today {
        background: rgba(52, 152, 219, 0.15) !important;
    }

    /* עיצוב הלופים (האירועים) */
    .fc-event {
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        padding: 5px !important;
        cursor: pointer !important;
        transition: transform 0.2s ease !important;
    }
    
    .fc-event:hover {
        transform: scale(1.05) !important;
        z-index: 100 !important;
    }

    /* עיצוב כותרת החודש */
    .fc-toolbar-title {
        color: white !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 10px rgba(52, 152, 219, 0.5);
    }

    /* עיצוב כפתורי ניווט */
    .fc-button {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 30px !important;
    }

    .fc-button-active {
        background: #3498db !important;
    }
    </style>
    """, unsafe_allow_html=True)

if "show_form" not in st.session_state:
    st.session_state.show_form = False

@st.cache_data(ttl=60)
def get_loop_data():
    res = supabase.table("loops").select("*").execute()
    return res.data

def get_color_by_name(name):
    # צבעים תוססים יותר
    colors = ["#00d2ff", "#92fe9d", "#ff758c", "#ff7eb3", "#8E2DE2", "#f9d423"]
    return colors[hash(name) % len(colors)]

st.markdown("<h1 style='text-align: center; color: white;'>LoopMate Vietnam 🇻🇳</h1>", unsafe_allow_html=True)

if st.session_state.show_form:
    # (הקוד של הטופס נשאר אותו דבר כמו קודם)
    st.markdown("<h2 style='text-align: center;'>🏍️ Create Your Loop</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("⬅️ Back to Calendar"):
            st.session_state.show_form = False
            st.rerun()
        with st.form("sexy_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                name = st.text_input("Name")
                phone = st.text_input("Phone Number")
                date = st.date_input("Start Date")
            with f_col2:
                duration = st.number_input("Days", min_value=1, value=3)
                size = st.number_input("Group Size", min_value=1, value=1)
                delete_code = st.text_input("Code", type="password")
            notes = st.text_area("Notes")
            if st.form_submit_button("LFG! 🚀"):
                if name and phone and delete_code:
                    clean_phone = phone.replace("-", "").replace(" ", "").replace("+", "")
                    if clean_phone.startswith("0"): clean_phone = "972" + clean_phone[1:]
                    data = {"name": name, "start_date": str(date), "duration_days": duration, "group_size": size, "phone": phone, "whatsapp_link": f"https://wa.me/{clean_phone}", "delete_code": delete_code, "notes": notes}
                    supabase.table("loops").insert(data).execute()
                    st.cache_data.clear()
                    st.session_state.show_form = False
                    st.rerun()
else:
    # כפתור הוספה
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("➕ Add My Loop"):
            st.session_state.show_form = True
            st.rerun()

    db_events = get_loop_data()
    calendar_events = []
    for ev in db_events:
        start = datetime.strptime(ev['start_date'], "%Y-%m-%d")
        end = start + timedelta(days=ev['duration_days'])
        calendar_events.append({
            "title": f"🏍️ {ev['name']} ({ev['group_size']})",
            "start": ev['start_date'],
            "end": end.strftime("%Y-%m-%d"),
            "backgroundColor": get_color_by_name(ev['name']),
            "extendedProps": {"wa_url": ev['whatsapp_link']}
        })

    # הגדרות לוח שנה - הוספנו תמיכה ב-LTR ושינוי יום התחלה לראשון
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
    with st.expander("🛠️ Manage My Posts"):
        m_col1, m_col2, m_col3 = st.columns([2,2,1])
        with m_col1:
            names = [ev['name'] for ev in db_events]
            name_to_del = st.selectbox("Select Name", names) if names else st.selectbox("Select Name", ["No loops found"])
        with m_col2:
            del_code = st.text_input("Enter Code", type="password", key="del_pwd")
        with m_col3:
            st.write(" ")
            if st.button("Delete"):
                target = next((item for item in db_events if item["name"] == name_to_del), None)
                if target and del_code == target['delete_code']:
                    supabase.table("loops").delete().eq("id", target['id']).execute()
                    st.cache_data.clear()
                    st.rerun()
