import streamlit as st
from supabase import create_client
from streamlit_calendar import calendar
from datetime import datetime, timedelta

# חיבור ל-Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Vietnam Loop Calendar", page_icon="📅", layout="wide")

st.title("📅 Vietnam Loop Finder")

# פונקציה לשליפת נתונים עם Cache - מונעת ריצה מיותרת מול ה-DB בכל קליק
@st.cache_data(ttl=60) # מתרענן אוטומטית כל דקה או כשקוראים ל-clear_cache
def get_loop_data():
    res = supabase.table("loops").select("*").execute()
    return res.data

# פונקציה לקביעת צבע קבוע לפי שם (כך שהצבע לא ישתנה בכל ריפרש)
def get_color_by_name(name):
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6", "#1abc9c", "#e67e22"]
    # משתמש בערך ה-Hash של השם כדי לבחור צבע קבוע לאותו אדם
    return colors[hash(name) % len(colors)]

# --- סרגל צד להוספה ---
with st.sidebar:
    st.header("➕ Add New Loop")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Name")
        phone = st.text_input("Phone number (e.g. 0501234567)")
        date = st.date_input("Start Date")
        duration = st.number_input("Duration (Days)", min_value=1, max_value=10, value=3)
        size = st.number_input("Group Size", min_value=1, value=1)
        delete_code = st.text_input("Personal Delete Code", type="password")
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Post Loop"):
            if name and phone and delete_code:
                clean_phone = phone.replace("-", "").replace(" ", "")
                if clean_phone.startswith("0"): clean_phone = "972" + clean_phone[1:]
                
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
                    st.cache_data.clear() # מנקה את הקאש כדי שהנתון החדש יופיע מיד
                    st.success("Posted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please fill in Name, Phone, and Delete Code")

# --- הכנת הנתונים ללוח השנה ---
db_events = get_loop_data()
calendar_events = []

for ev in db_events:
    start = datetime.strptime(ev['start_date'], "%Y-%m-%d")
    end = start + timedelta(days=ev['duration_days'])
    display_title = f"{ev['name']} - {ev['group_size']} ppl - {ev['phone']}"
    
    calendar_events.append({
        "title": display_title,
        "start": ev['start_date'],
        "end": end.strftime("%Y-%m-%d"),
        "backgroundColor": get_color_by_name(ev['name']), # צבע קבוע לפי שם
        "borderColor": get_color_by_name(ev['name']),
        "resource": ev
    })

# --- הגדרות לוח שנה ---
calendar_options = {
    "initialView": "dayGridMonth",
    "direction": "ltr",
    "firstDay": 0,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,dayGridWeek"
    },
    "navLinks": True,
}

# שימוש ב-Key קבוע ללוח השנה מונע ממנו להיבנות מחדש בכל אינטראקציה
state = calendar(events=calendar_events, options=calendar_options, key="loop_calendar")

# --- הצגת פרטים ומחיקה ---
if state.get("eventClick"):
    ev_data = state["eventClick"]["event"]["extendedProps"]["resource"]
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Details: {ev_data['name']}")
        st.write(f"👥 Group Size: {ev_data['group_size']}")
        st.write(f"📞 Phone: {ev_data['phone']}")
        if ev_data['notes']: st.info(f"📝 Notes: {ev_data['notes']}")
        st.link_button("Chat on WhatsApp 💬", ev_data['whatsapp_link'])
    with col2:
        st.subheader("🗑️ Delete My Entry")
        input_code = st.text_input("Enter delete code", type="password", key="del_key")
        if st.button("Delete Permanently"):
            if input_code == ev_data['delete_code']:
                supabase.table("loops").delete().eq("id", ev_data['id']).execute()
                st.cache_data.clear() # מנקה קאש אחרי מחיקה
                st.success("Deleted!")
                st.rerun()
            else:
                st.error("Incorrect code")
