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
        return requests.post(url, data=payload).status_code == 200
    except: return False

# --- 2. የገጽ ዝግጅት ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

# የትዕዛዝ ቅርጫት ዝግጅት (Session State)
if 'cart' not in st.session_state:
    st.session_state.cart = []

menu = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

st.title("🍳 እሙ ምግብ ቤት")

# --- 3. ምግብ መምረጫ ክፍል ---
st.subheader("🍕 ምግቦችን ይምረጡ")
col_f, col_q, col_b = st.columns([3, 1, 1])

with col_f:
    food_to_add = st.selectbox("ምግብ ይምረጡ", list(menu.keys()), label_visibility="collapsed")
with col_q:
    qty_to_add = st.number_input("ብዛት", min_value=1, value=1, step=1, label_visibility="collapsed")
with col_b:
    if st.button("ጨምር ➕"):
        st.session_state.cart.append({
            "name": food_to_add,
            "qty": qty_to_add,
            "price": menu[food_to_add] * qty_to_add
        })
        st.toast(f"{food_to_add} ተጨምሯል!")

# --- 4. የተመረጡ ምግቦች ዝርዝር (Cart Display) ---
if st.session_state.cart:
    st.write("---")
    st.subheader("🛒 የእርስዎ ትዕዛዞች")
    
    total_bill = 0
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
        c1.write(item['name'])
        c2.write(f"x{item['qty']}")
        c3.write(f"{item['price']:.2f} ብር")
        if c4.button("❌", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()
        total_bill += item['price']
    
    st.markdown(f"### 💰 ጠቅላላ ሂሳብ: **{total_bill:.2f} ብር**")
    
    if st.button("የመረጥኩትን አዝዝ 🚀"):
        customer_name = st.text_input("የእርስዎ ስም (ለማረጋገጫ ያህል)")
        telegram_username = st.text_input("የቴሌግራም መለያ (@...)")
        
        if customer_name and telegram_username:
            order_id = datetime.now().strftime("%H%M%S")
            clean_user = telegram_username.replace("@", "").strip()
            
            # የትዕዛዝ ዝርዝር ለቴሌግራም
            items_text = ""
            for item in st.session_state.cart:
                items_text += f"• {item['name']} (x{item['qty']}) - {item['price']} ብር\n"
            
            owner_msg = (
                f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n\n"
                f"👤 <b>ደንበኛ:</b> {customer_name}\n"
                f"🍲 <b>ዝርዝር:</b>\n{items_text}\n"
                f"💵 <b>ጠቅላላ:</b> {total_bill} ብር\n\n"
                f"✅ <a href='https://t.me/{clean_user}'>ምላሽ ስጥ</a>"
            )
            
            if send_telegram_msg(owner_msg):
                st.success("✅ ትዕዛዝዎ በተሳካ ሁኔታ ተልኳል!")
                st.session_state.cart = [] # ቅርጫቱን ባዶ ማድረግ
                st.balloons()
            else:
                st.error("ትዕዛዙ አልተላከም::")
        else:
            st.info("እባክዎ ስም እና ቴሌግራም ያስገቡ")
else:
    st.info("ምንም የተመረጠ ምግብ የለም። ከላይ ይምረጡና 'ጨምር' የሚለውን ይጫኑ።")
