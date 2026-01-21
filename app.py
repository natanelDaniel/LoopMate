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
                clean_phone = phone.replace("-", "").replace(" ", "").replace("+", "")
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
    
    # שינוי פורמט הכותרת לפי בקשתך
    display_title = f"{ev['name']} - {ev['group_size']} איש - {ev['phone']}"
    
    calendar_events.append({
        "title": display_title,
        "start": ev['start_date'],
        "end": end.strftime("%Y-%m-%d"),
        "backgroundColor": get_color_by_name(ev['name']),
        "borderColor": get_color_by_name(ev['name']),
        # הסרנו את ה-URL מכאן כדי למנוע את השגיאה שראית בתמונה
        "extendedProps": {"wa_url": ev['whatsapp_link']}
    })

# --- הגדרות לוח שנה ---
calendar_options = {
    "initialView": "dayGridMonth",
    "direction": "rtl",
    "firstDay": 0,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,dayGridWeek"
    }
}

st.title("🇻🇳 Vietnam Loop Finder")
st.info("💡 לחיצה על לופ תפתח מיד את הוואטסאפ של המפרסם בחלון חדש")

# תצוגת לוח השנה - שימוש ב-Key קבוע
state = calendar(events=calendar_events, options=calendar_options, key="loop_calendar")

# --- הפתרון ללחיצה: פתיחת חלון חדש דרך פייתון ---
if state.get("eventClick"):
    # שליפת הלינק מתוך ה-Extended Props ששמרנו
    wa_url = state["eventClick"]["event"]["extendedProps"]["wa_url"]
    
    # הזרקת קוד JS קטן שפותח טאב חדש באמת
    st.components.v1.html(
        f"""
        <script>
            window.open('{wa_url}', '_blank');
        </script>
        """,
        height=0,
    )

# --- אזור מחיקה ---
st.divider()
with st.expander("🗑️ למחיקת הפרסום שלך"):
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        names = [ev['name'] for ev in db_events]
        name_to_del = st.selectbox("בחר שם", names)
    with col2:
        del_code = st.text_input("קוד אישי", type="password", key="del_pwd")
    with col3:
        st.write(" ")
        if st.button("מחק לצמיתות"):
            target = next((item for item in db_events if item["name"] == name_to_del), None)
            if target and del_code == target['delete_code']:
                supabase.table("loops").delete().eq("id", target['id']).execute()
                st.cache_data.clear()
                st.success("הפרסום נמחק")
                st.rerun()
            else:
                st.error("קוד שגוי")
