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

# 1. טופס הוספה בסרגל הצד
with st.sidebar:
    st.header("➕ הוסף לופ חדש")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("שם")
        date = st.date_input("תאריך יציאה")
        duration = st.number_input("כמה ימים הלופ?", min_value=1, max_value=10, value=3)
        size = st.number_input("מספר משתתפים", min_value=1, value=1)
        phone = st.text_input("וואטסאפ (למשל 0501234567)")
        delete_code = st.text_input("קוד אישי למחיקה (זכור אותו!)", type="password")
        notes = st.text_area("הערות")
        
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
                st.success("הלופ פורסם בהצלחה!")
                st.rerun()
            else:
                st.error("נא למלא שם, טלפון וקוד אישי")

# 2. שליפת נתונים והכנה ללוח שנה
res = supabase.table("loops").select("*").execute()
db_events = res.data

calendar_events = []
for ev in db_events:
    start = datetime.strptime(ev['start_date'], "%Y-%m-%d")
    end = start + timedelta(days=ev['duration_days'])
    
    # התצוגה שביקשת בתוך הלוח שנה
    display_title = f"{ev['name']} - {ev['group_size']} משתתפים - {ev['phone']}"
    
    calendar_events.append({
        "title": display_title,
        "start": ev['start_date'],
        "end": end.strftime("%Y-%m-%d"),
        "resource": ev
    })

# 3. הגדרות ותצוגת לוח שנה
calendar_options = {"initialView": "dayGridMonth", "direction": "rtl"}
state = calendar(events=calendar_events, options=calendar_options)

# 4. הצגת פרטים ואפשרות מחיקה בלחיצה
if state.get("eventClick"):
    ev_data = state["eventClick"]["event"]["extendedProps"]["resource"]
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"פרטים: {ev_data['name']}")
        st.write(f"👥 **משתתפים:** {ev_data['group_size']}")
        st.write(f"📞 **טלפון:** {ev_data['phone']}")
        st.write(f"📅 **תאריך:** {ev_data['start_date']} ({ev_data['duration_days']} ימים)")
        st.link_button("שלח הודעה בוואטסאפ 💬", ev_data['whatsapp_link'])
    
    with col2:
        st.subheader("🗑️ מחיקת הלופ שלי")
        input_code = st.text_input("הכנס קוד אישי למחיקה", type="password", key="del_input")
        if st.button("מחק לופ לצמיתות"):
            if input_code == ev_data['delete_code']:
                supabase.table("loops").delete().eq("id", ev_data['id']).execute()
                st.success("הלופ נמחק!")
                st.rerun()
            else:
                st.error("קוד שגוי")
