import streamlit as st
from supabase import create_client
from streamlit_calendar import calendar
from datetime import datetime, timedelta

# חיבור ל-Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Vietnam Loop Calendar", page_icon="📅", layout="wide")

st.title("📅 לוח לופים - ויטנאם")

# 1. טופס הוספה
with st.sidebar:
    st.header("➕ הוסף לופ חדש")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("שם")
        date = st.date_input("תאריך יציאה")
        duration = st.number_input("כמה ימים הלופ?", min_value=1, max_value=10, value=3)
        phone = st.text_input("וואטסאפ (למשל 0501234567)")
        notes = st.text_area("הערות")
        
        if st.form_submit_button("פרסם"):
            clean_phone = phone.replace("-", "").replace(" ", "")
            if clean_phone.startswith("0"): clean_phone = "972" + clean_phone[1:]
            
            data = {
                "name": name, 
                "start_date": str(date), 
                "duration_days": duration,
                "phone": phone,
                "whatsapp_link": f"https://wa.me/{clean_phone}",
                "notes": notes
            }
            supabase.table("loops").insert(data).execute()
            st.success("פורסם!")
            st.rerun()

# 2. שליפת נתונים והכנה ללוח שנה
res = supabase.table("loops").select("*").execute()
db_events = res.data

calendar_events = []
for ev in db_events:
    start = datetime.strptime(ev['start_date'], "%Y-%m-%d")
    end = start + timedelta(days=ev['duration_days'])
    
    calendar_events.append({
        "title": f"🏍️ {ev['name']}",
        "start": ev['start_date'],
        "end": end.strftime("%Y-%m-%d"),
        "resource": ev # שומרים את כל המידע בתוך האיוונט
    })

# 3. הגדרות לוח שנה
calendar_options = {
    "editable": False,
    "selectable": True,
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,dayGridWeek",
    },
    "initialView": "dayGridMonth",
    "direction": "rtl",
}

# הצגת לוח השנה
state = calendar(events=calendar_events, options=calendar_options)

# 4. הצגת פרטים בלחיצה
if state.get("eventClick"):
    ev_data = state["eventClick"]["event"]["extendedProps"]["resource"]
    st.divider()
    st.subheader(f"פרטים על הלופ של {ev_data['name']}")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"📅 **תאריך יציאה:** {ev_data['start_date']}")
        st.write(f"⏳ **משך הלופ:** {ev_data['duration_days']} ימים")
        st.write(f"📞 **טלפון:** {ev_data['phone']}")
    with col2:
        st.write(f"📝 **הערות:** {ev_data['notes'] or 'אין'}")
        st.link_button("דברו איתי בוואטסאפ 💬", ev_data['whatsapp_link'])
