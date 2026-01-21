import streamlit as st
from supabase import create_client
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import random

# חיבור ל-Supabase (וודא שה-Secrets מוגדרים)
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Vietnam Loop Calendar", page_icon="📅", layout="wide")

st.title("📅 Vietnam Loop Finder")

# פונקציה לייצור צבע רנדומלי לכל לופ
def get_random_color():
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6", "#1abc9c", "#e67e22"]
    return random.choice(colors)

# --- סרגל צד להוספה עם סדר שדות חדש ---
with st.sidebar:
    st.header("➕ Add New Loop")
    with st.form("add_form", clear_on_submit=True):
        # 1. שם
        name = st.text_input("Name")
        
        # 2. מספר טלפון
        phone = st.text_input("WhatsApp (e.g. 0501234567)")
        
        # 3. תאריך
        date = st.date_input("Start Date")
        
        # 4. שאר השדות
        duration = st.number_input("Duration (Days)", min_value=1, max_value=10, value=3)
        size = st.number_input("Group Size", min_value=1, value=1)
        delete_code = st.text_input("Personal Delete Code", type="password")
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Post Loop"):
            if name and phone and delete_code:
                # ניקוי והכנת מספר הטלפון
                clean_phone = phone.replace("-", "").replace(" ", "")
                if clean_phone.startswith("0"): 
                    clean_phone = "972" + clean_phone[1:]
                
                data = {
                    "name": name, 
                    "start_date": str(date), 
                    "duration_days": duration,
                    "group_size": size,
                    "phone": phone,
                    "whatsapp_link": f"https://wa.me/{clean_phone}",
                    "delete_code": delete_code,
                    "notes": notes
                }
                
                try:
                    supabase.table("loops").insert(data).execute()
                    st.success("Posted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please fill in Name, Phone, and Delete Code")
# --- הכנת הנתונים ללוח השנה ---
res = supabase.table("loops").select("*").execute()
db_events = res.data

calendar_events = []
for ev in db_events:
    start = datetime.strptime(ev['start_date'], "%Y-%m-%d")
    end = start + timedelta(days=ev['duration_days'])
    
    # התצוגה שביקשת: שם - משתתפים - טלפון
    display_title = f"{ev['name']} - {ev['group_size']} ppl - {ev['phone']}"
    
    calendar_events.append({
        "title": display_title,
        "start": ev['start_date'],
        "end": end.strftime("%Y-%m-%d"),
        "backgroundColor": get_random_color(),
        "resource": ev
    })

# --- הגדרות לוח שנה (Ltr ויום ראשון) ---
calendar_options = {
    "initialView": "dayGridMonth",
    "direction": "ltr",          # תצוגה משמאל לימין
    "firstDay": 0,               # 0 מייצג את יום ראשון (Sunday)
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,dayGridWeek"
    }
}

# תצוגת לוח השנה
state = calendar(events=calendar_events, options=calendar_options)

# --- הצגת פרטים ומחיקה ---
if state.get("eventClick"):
    ev_data = state["eventClick"]["event"]["extendedProps"]["resource"]
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Details: {ev_data['name']}")
        st.write(f"👥 Group Size: {ev_data['group_size']}")
        st.write(f"📞 Phone: {ev_data['phone']}")
        st.link_button("Chat on WhatsApp 💬", ev_data['whatsapp_link'])
    with col2:
        st.subheader("🗑️ Delete My Entry")
        input_code = st.text_input("Enter delete code", type="password", key="del_key")
        if st.button("Delete Permanently"):
            if input_code == ev_data['delete_code']:
                supabase.table("loops").delete().eq("id", ev_data['id']).execute()
                st.success("Deleted!")
                st.rerun()
            else:
                st.error("Incorrect code")
