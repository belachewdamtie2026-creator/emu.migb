import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import qrcode
from io import BytesIO

# --- 1. ኮንፊገሬሽን (Telegram) ---
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
    .stApp { background-color: #fdfdfd; }
    .main-header { text-align: center; color: #E64A19; font-weight: bold; margin-bottom: 0px; }
    .sub-header { text-align: center; color: #757575; font-size: 14px; margin-bottom: 20px; }
    .order-box {
        background-color: white; padding: 15px; border-radius: 12px;
        margin-bottom: 10px; border-left: 6px solid #E64A19;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        display: flex; justify-content: space-between; align-items: center;
    }
    div.stButton > button {
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

MENU = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

# --- Sidebar ---
st.sidebar.markdown("<h2 style='text-align: center;'>🍱 እሙ ምግብ ቤት</h2>", unsafe_allow_html=True)
app_url = "https://emumigb-2018.streamlit.app/" 
qr_img = qrcode.make(app_url)
buf = BytesIO()
qr_img.save(buf, format="PNG")
st.sidebar.image(buf.getvalue(), caption="በስልክዎ ስካን አድርገው ይዘዙ")

# --- ዋናው ክፍል ---
st.markdown("<h1 class='main-header'>🍳 እሙ ምግብ ቤት</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>ትዕዛዝዎን ያስገቡ፤ በቀጥታ ወደ እኛ ይደርሳል!</p>", unsafe_allow_html=True)

if 'cart' not in st.session_state:
    st.session_state.cart = []

col_a, col_b = st.columns(2)
first_name = col_a.text_input("👤 ስም", placeholder="የመጀመሪያ ስም")
c_tele = col_b.text_input("💬 ስልክ/ቴሌግራም", placeholder="09...")

st.divider()

# ከአንድ በላይ ምግብ መምረጥ እንዲቻል multiselect ተደርጓል
selected_foods = st.multiselect("ምግቦችን ይምረጡ (ከአንድ በላይ መምረጥ ይችላሉ)", list(MENU.keys()))
qty = st.number_input("የእያንዳንዱ ብዛት", 1, 20, 1)

if st.button("ወደ ቅርጫት ጨምር 🛒", use_container_width=True):
    if selected_foods:
        for f in selected_foods:
            st.session_state.cart.append({"ምግብ": f, "ብዛት": qty, "ዋጋ": MENU[f]*qty})
        st.toast(f"✅ {len(selected_foods)} አይነት ምግቦች ተጨምረዋል")
    else:
        st.warning("እባክዎ መጀመሪያ ምግብ ይምረጡ")

if st.session_state.cart:
    st.markdown("---")
    display_title = f"🛒 የ{first_name} ምርጫዎች" if first_name else "🛒 የያዙት ምግቦች"
    st.markdown(f"### {display_title}")
    
    total_bill = 0
    summary = ""
    
    for i, item in enumerate(st.session_state.cart):
        with st.container():
            col_item, col_del = st.columns([4, 1])
            col_item.markdown(f"""
                <div class='order-box'>
                    <span><b>{item['ምግብ']}</b> (x{item['ብዛት']})</span>
                    <span style='color: #E64A19; font-weight: bold;'>{item['ዋጋ']:.2f} ብር</span>
                </div>
            """, unsafe_allow_html=True)
            if col_del.button("❌", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
        
        total_bill += item['ዋጋ']
        summary += f"• {item['ምግብ']} (x{item['ብዛት']}) - {item['ዋጋ']} ብር\n"
    
    st.markdown(f"<h2 style='text-align:right; color:#E64A19;'>ጠቅላላ: {total_bill:.2f} ብር</h2>", unsafe_allow_html=True)
    
    if st.button("ትዕዛዝ አስተላልፍ 🚀", use_container_width=True):
        if first_name:
            msg = f"🔔 <b>አዲስ ትዕዛዝ ከዌብሳይት</b>\n\n👤 <b>ደንበኛ:</b> {first_name}\n📞 <b>ስልክ:</b> {c_tele}\n\n📝 <b>ዝርዝር:</b>\n{summary}\n💰 <b>ጠቅላላ: {total_bill} ብር</b>"
            send_telegram_msg(msg)
            st.success(f"እናመሰግናለን {first_name}! ትዕዛዝዎ በተሳካ ሁኔታ ተልኳል።")
            st.session_state.cart = []
            st.balloons()
        else:
            st.warning("እባክዎ ትዕዛዙን ከማስተላለፍዎ በፊት ስምዎን ያስገቡ")

st.markdown(f"<p style='text-align:center; color:#718096; font-size:11px; margin-top:50px;'>Developed by <b>Belachew Damtie</b></p>", unsafe_allow_html=True)
