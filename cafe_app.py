import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import qrcode
from io import BytesIO

# --- 1. ኮንፊገሬሽን (Telegram) ---
# እዚህ ጋር የእርስዎን BOT_TOKEN እና CHAT_ID ያስገቡ
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
CHAT_ID = "1066005872"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=5)
    except:
        pass

# --- 2. ገጽ ዝግጅት ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #f5f7f8; }
    .main-header { text-align: center; color: #FF5722; font-weight: bold; }
    .order-box {
        background-color: white; padding: 15px; border-radius: 12px;
        margin-bottom: 10px; border-left: 6px solid #FF5722;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

MENU = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

# --- Sidebar ---
st.sidebar.title("🍱 እሙ ምግብ ቤት")
app_url = "https://emumigb-2018.streamlit.app/" 
qr_img = qrcode.make(app_url)
buf = BytesIO()
qr_img.save(buf, format="PNG")
st.sidebar.image(buf.getvalue(), caption="በስልክዎ ስካን አድርገው ይዘዙ")

# --- ዋናው ክፍል ---
st.markdown("<h1 class='main-header'>🍳 እሙ ምግብ ቤት</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>ትዕዛዝዎን ያስገቡ፤ በቀጥታ ወደ እኛ ይደርሳል!</p>", unsafe_allow_html=True)

if 'cart' not in st.session_state:
    st.session_state.cart = []

col_a, col_b = st.columns(2)
c_name = col_a.text_input("👤 ስም")
c_tele = col_b.text_input("💬 ስልክ/ቴሌግራም")

col_f, col_q = st.columns([3, 1])
food = col_f.selectbox("ምግብ ይምረጡ", list(MENU.keys()))
qty = col_q.number_input("ብዛት", 1, 20, 1)

if st.button("ወደ ቅርጫት ጨምር 🛒", use_container_width=True):
    st.session_state.cart.append({"ምግብ": food, "ብዛት": qty, "ዋጋ": MENU[food]*qty})
    st.toast(f"✅ {food} ተጨምሯል")

if st.session_state.cart:
    st.divider()
    st.markdown("### 🛒 የያዙት ምግቦች")
    total_bill = 0
    summary = ""
    for i, item in enumerate(st.session_state.cart):
        st.markdown(f"<div class='order-box'><b>{item['ምግብ']}</b> (x{item['ብዛት']}) <span style='float:right;'>{item['ዋጋ']} ብር</span></div>", unsafe_allow_html=True)
        total_bill += item['ዋጋ']
        summary += f"• {item['ምግብ']} (x{item['ብዛት']})\n"
        if st.button(f"ሰርዝ", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()
    
    st.markdown(f"<h2 style='text-align:right; color:#FF5722;'>ጠቅላላ: {total_bill} ብር</h2>", unsafe_allow_html=True)
    
    if st.button("ትዕዛዝ አስተላልፍ 🚀", use_container_width=True):
        if c_name:
            msg = f"🔔 <b>አዲስ ትዕዛዝ ከዌብሳይት</b>\n\n👤 <b>ደንበኛ:</b> {c_name}\n📞 <b>ስልክ:</b> {c_tele}\n\n📝 <b>ዝርዝር:</b>\n{summary}\n💰 <b>ጠቅላላ: {total_bill} ብር</b>"
            send_telegram_msg(msg)
            st.success("ትዕዛዝዎ በተሳካ ሁኔታ ተልኳል! እናመሰግናለን።")
            st.session_state.cart = []
            st.balloons()
        else:
            st.warning("እባክዎ ስምዎን ያስገቡ")
