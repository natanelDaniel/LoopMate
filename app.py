import streamlit as st
from supabase import create_client

# חיבור ל-Supabase
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Vietnam Loop Finder", page_icon="🇻🇳", layout="centered")

# עיצוב כותרת
st.title("🇻🇳 מוצא השותפים ללופ")
st.markdown("---")

# טופס להוספת לופ
with st.expander("➕ הוסף את הלופ שלך - לחץ כאן"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("שם מלא / כינוי")
        date = st.date_input("תאריך יציאה ללופ")
        size = st.number_input("כמה אנשים אתם כרגע?", min_value=1, value=1)
        phone = st.text_input("מספר טלפון (למשל: 0501234567)")
        notes = st.text_area("פרטים נוספים (למשל: 'מחפשים נהגים', 'בני 24-26', 'יוצאים מהא ז'אנג')")
        
        submitted = st.form_submit_button("פרסם לופ ✅")
        
        if submitted:
            if name and phone:
                # ניקוי המספר ליצירת לינק וואטסאפ תקין
                clean_phone = phone.replace("-", "").replace(" ", "")
                if clean_phone.startswith("0"):
                    clean_phone = "972" + clean_phone[1:]
                
                wa_link = f"https://wa.me/{clean_phone}"
                
                data = {
                    "name": name, 
                    "start_date": str(date), 
                    "group_size": size, 
                    "phone": phone, # המספר כפי שהוקלד
                    "whatsapp_link": wa_link,
                    "notes": notes
                }
                
                try:
                    supabase.table("loops").insert(data).execute()
                    st.success("הלופ פורסם בהצלחה! רענן את העמוד כדי לראות.")
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה בשמירה: {e}")
            else:
                st.warning("חובה למלא שם ומספר טלפון")

# תצוגת הלופים
st.subheader("📍 מחפשים שותפים:")

# שליפת נתונים - סינון לופים שעברו (אופציונלי)
from datetime import date as dt_date
today = str(dt_date.today())

res = supabase.table("loops").select("*").filter("start_date", "gte", today).order("start_date").execute()
loops = res.data

if not loops:
    st.info("אין לופים רשומים כרגע. תהיה הראשון לפרסם!")
else:
    for loop in loops:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {loop['name']}")
                st.markdown(f"📅 **תאריך:** {loop['start_date']} | 👥 **כמות:** {loop['group_size']}")
                st.markdown(f"📞 **טלפון:** {loop['phone']}")
                if loop['notes']:
                    st.caption(f"💬 {loop['notes']}")
            with col2:
                st.write("") # מרווח
                st.link_button("וואטסאפ 💬", loop['whatsapp_link'], use_container_width=True)

# הערה בתחתית
st.markdown("---")
st.caption("המידע נמחק אוטומטית לאחר שעובר תאריך הלופ (בקרוב)")
