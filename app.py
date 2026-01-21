import streamlit as st
from supabase import create_client
from streamlit_calendar import calendar
from datetime import datetime, timedelta

# חיבור ל-Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Vietnam Loop Calendar", page_icon="📅", layout="wide")

# פונקציה לשליפת נתונים עם Cache
@st.cache_data(ttl=60)
def get_loop_data():
    res = supabase.table("loops").select("*").execute()
    return res.data

# פונקציה לקביעת צבע קבוע לפי שם
def get_color_by_name(name):
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6", "#1abc9c", "#e67e22"]
    return colors[hash(name) % len(colors)]

# --- סרגל צד להוספה ---
with st.sidebar:
    st.header("➕ הוספת לופ חדש")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("שם")
        phone = st.text_input("מספר טלפון (למשל 0501234567)")
        date = st.date_input("תאריך יציאה")
        duration = st.number_input("כמה ימים הלופ?", min_value=1, max_value=10, value=3)
        size = st.number_input("כמה אנשים אתם?", min_value=1, value=1)
        delete_code = st.text_input("קוד אישי למחיקה", type="password")
        notes = st.text_area("הערות נוספות")
        
        if st.form_submit_button("פרסם לופ"):
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
                supabase.table("loops").insert(data).execute()
                st.cache_data.clear()
                st.success("הלופ פורסם!")
                st.rerun()

# --- הכנת הנתונים ללוח השנה ---
db_events = get_loop_data()
calendar_events = []

for ev in db_events:
    start = datetime.strptime(ev['start_date'], "%Y-%m-%d")
    end = start + timedelta(days=ev['duration_days'])
    
    # סידור הטקסט עם תמיכה בעברית (RTL) - שם, אז משתתפים, אז טלפון
    display_title = f"{ev['phone']} - {ev['group_size']} איש - {ev['name']}"
    
    calendar_events.append({
        "title": display_title,
        "start": ev['start_date'],
        "end": end.strftime("%Y-%m-%d"),
        "backgroundColor": get_color_by_name(ev['name']),
        "url": ev['whatsapp_link'], # הופך את כל האירוע ללחיץ ישירות לוואטסאפ
        "resource": ev
    })

# --- הגדרות לוח שנה ---
calendar_options = {
    "initialView": "dayGridMonth",
    "direction": "rtl",          # מעביר את כל הלוח למצב ימין לשמאל
    "firstDay": 0,               # יום ראשון בתחילת שבוע
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,dayGridWeek"
    }
}

st.title("🇻🇳 Vietnam Loop Finder")

# תצוגת לוח השנה
state = calendar(events=calendar_events, options=calendar_options, key="loop_calendar")

# --- אזור מחיקה (למטה) ---
st.divider()
st.subheader("🗑️ מחיקת לופ קיים")
with st.expander("לחץ כאן כדי למחוק את הפרסום שלך"):
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        # יצירת רשימת שמות למחיקה
        names = [ev['name'] for ev in db_events]
        name_to_del = st.selectbox("בחר שם למחיקה", names)
    with col2:
        del_code = st.text_input("הכנס קוד אישי", type="password")
    with col3:
        st.write(" ") # מרווח
        if st.button("מחק"):
            # מוצא את האירוע המתאים
            target = next((item for item in db_events if item["name"] == name_to_del), None)
            if target and del_code == target['delete_code']:
                supabase.table("loops").delete().eq("id", target['id']).execute()
                st.cache_data.clear()
                st.success("נמחק!")
                st.rerun()
            else:
                st.error("קוד שגוי")
