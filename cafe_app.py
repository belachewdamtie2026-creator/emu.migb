import streamlit as st
from datetime import datetime
import requests
import urllib.parse

# --- 1. የቴሌግራም መረጃ ---
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
CHAT_ID = "1066005872"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except:
        pass

# --- 2. ዳታቤዝ (በጊዜያዊነት በ Session State) ---
# በቋሚነት እንዲቀመጥ ወደፊት Google Sheet ይታከላል
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "አህመድ መሀመድ": "1234",
        "ሳራ ካሳ": "5678"
    }

if 'logs' not in st.session_state:
    st.session_state.logs = []

menu = {"በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00, "ጥብስ": 200.00}

# --- 3. ገጽ ዝግጅት ---
st.set_page_config(page_title="እሙ ቋሚ መፈረሚያ", page_icon="📝")

tab1, tab2 = st.tabs(["👤 የደንበኞች መፈረሚያ", "⚙️ የባለቤት መቆጣጠሪያ"])

# --- 4. የደንበኞች መፈረሚያ (Tab 1) ---
with tab1:
    st.header("📝 የቋሚ ተመጋቢዎች ፊርማ")
    
    names = ["ስምዎን ይምረጡ..."] + list(st.session_state.users_db.keys())
    selected_user = st.selectbox("ስም", names)
    pin_input = st.text_input("የይለፍ ቃል (PIN)", type="password", key="user_pin")

    if selected_user != "ስምዎን ይምረጡ...":
        st.subheader(f"ሰላም {selected_user}፣ የተመገቡትን ይምረጡ")
        selected_foods = st.multiselect("ምግቦች", list(menu.keys()))
        
        if st.button("አረጋግጣለሁ (ፈርሜያለሁ) ✍️"):
            if pin_input == st.session_state.users_db[selected_user]:
                if selected_foods:
                    total_price = sum(menu[f] for f in selected_foods)
                    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    # ለባለቤቱ መልእክት መላክ
                    tg_msg = (f"<b>✅ አዲስ ዲጂታል ፊርማ</b>\n\n"
                              f"👤 <b>ደንበኛ:</b> {selected_user}\n"
                              f"🍽 <b>ምግቦች:</b> {', '.join(selected_foods)}\n"
                              f"💰 <b>ድምር ሂሳብ:</b> {total_price} ብር\n"
                              f"📅 <b>ቀን:</b> {time_now}")
                    
                    send_telegram_msg(tg_msg)
                    
                    # ለጊዜው እዚህ መመዝገብ
                    st.session_state.logs.append({
                        "ቀን": time_now, "ደንበኛ": selected_user, 
                        "ምግብ": ", ".join(selected_foods), "ሂሳብ": total_price
                    })
                    
                    st.success(f"በተሳካ ሁኔታ ተፈርሟል! ለባለቤቱ ተልኳል።")
                    st.balloons()
                else:
                    st.error("እባክዎ መጀመሪያ ምግብ ይምረጡ!")
            else:
                st.error("የይለፍ ቃል ስህተት ነው!")

# --- 5. የባለቤት ክፍል (Tab 2) ---
with tab2:
    st.header("⚙️ የአስተዳዳሪ ክፍል")
    admin_pin = st.text_input("የባለቤት መለያ ቁጥር ያስገቡ", type="password")
    
    if admin_pin == "admin123": # የባለቤቱ ሚስጥር ቁጥር
        st.divider()
        st.subheader("➕ አዲስ ደንበኛ መመዝገቢያ")
        new_name = st.text_input("የደንበኛ ሙሉ ስም")
        new_pin = st.text_input("የሚሰጣቸው የይለፍ ቃል (PIN)")
        
        if st.button("መዝግብ"):
            if new_name and new_pin:
                st.session_state.users_db[new_name] = new_pin
                st.success(f"{new_name} በተሳካ ሁኔታ ተመዝግቧል!")
                st.rerun()
        
        st.divider()
        st.subheader("📜 የዛሬ የፊርማ ታሪክ")
        if st.session_state.logs:
            st.table(st.session_state.logs)
        else:
            st.info("እስካሁን የተመዘገበ ፊርማ የለም።")
    elif admin_pin:
        st.error("የባለቤት መለያ ቁጥር ተሳስቷል!")
