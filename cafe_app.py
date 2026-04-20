import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import qrcode
from io import BytesIO
import time

# --- 1. ኮንፊገሬሽን (Telegram) ---
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
CHAT_ID = "1066005872"

# ትዕዛዞችን ለመከታተል (በጊዜያዊነት በsession state ይያዛል)
if 'order_status' not in st.session_state:
    st.session_state.order_status = "በመጠባበቅ ላይ..."

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # በቴሌግራም ለባለቤቱ የሚመጡ ምርጫዎች (Buttons)
    keyboard = {
        "inline_keyboard": [[
            {"text": "አለ (ተቀበል) ✅", "callback_data": "accept"},
            {"text": "የለም (ሰርዝ) ❌", "callback_data": "reject"}
        ]]
    }
    
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "HTML",
        "reply_markup": keyboard
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass

# የባለቤቱን ምላሽ ለመፈተሽ (Poll)
def check_for_response():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url, timeout=5).json()
        if response["result"]:
            # የመጨረሻውን የባለቤት ምላሽ መፈለግ
            for update in reversed(response["result"]):
                if "callback_query" in update:
                    res = update["callback_query"]["data"]
                    if res == "accept":
                        return "ትዕዛዝዎ ተቀባይነት አግኝቷል! በቅርቡ ይደርሳል። ✅"
                    elif res == "reject":
                        return "ይቅርታ፣ ያዘዙት ምግብ ለጊዜው አልቋል። ❌"
    except:
        pass
    return None

# --- 2. ገጽ ዝግጅት ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #fdfdfd; }
    .main-header { text-align: center; color: #E64A19; font-weight: bold; }
    .order-box {
        background-color: white; padding: 15px; border-radius: 12px;
        margin-bottom: 10px; border-left: 6px solid #E64A19;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .status-card {
        background-color: #fff3e0; padding: 15px; border-radius: 10px;
        text-align: center; border: 1px solid #ffb74d; margin-top: 20px;
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

if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'last_order_sent' not in st.session_state:
    st.session_state.last_order_sent = False

col_a, col_b = st.columns(2)
first_name = col_a.text_input("👤 ስም", placeholder="የመጀመሪያ ስም")
c_tele = col_b.text_input("💬 ስልክ/ቴሌግራም", placeholder="09...")

st.divider()

packing_style = st.radio("**የአቀራረብ ሁኔታ ይምረጡ**", ["ለየብቻ", "በአንድ እቃ"], horizontal=True)

food_items_to_add = []
if packing_style == "በአንድ እቃ":
    selected_foods = st.multiselect("በአንድ እቃ የሚቀላቀሉ ምግቦችን ይምረጡ", list(MENU.keys()))
    if selected_foods:
        for f in selected_foods:
            c1, c2 = st.columns([3, 1])
            with c1: st.write(f"**{f}**")
            qty = c2.number_input("ብዛት", 1, 10, 1, key=f"mixed_{f}", label_visibility="collapsed")
            food_items_to_add.append({"ምግብ": f, "ብዛት": qty})
else:
    f = st.selectbox("የሚፈልጉትን ምግብ ይምረጡ", list(MENU.keys()))
    qty = st.number_input("ብዛት", 1, 20, 1)
    food_items_to_add.append({"ምግብ": f, "ብዛት": qty})

if st.button("ወደ ቅርጫት ጨምር 🛒", use_container_width=True):
    if food_items_to_add:
        if packing_style == "በአንድ እቃ":
            details = ", ".join([f"{i['ምግብ']} (x{i['q']})" for i in food_items_to_add])
            price = sum([MENU[i['ምግብ']] * i['ብዛት'] for i in food_items_to_add])
            st.session_state.cart.append({"ዝርዝር": details, "ሁኔታ": "በአንድ እቃ", "ዋጋ": price})
        else:
            for i in food_items_to_add:
                st.session_state.cart.append({"ዝርዝር": f"{i['ምግብ']} (x{i['ብዛት']})", "ሁኔታ": "ለየብቻ", "ዋጋ": MENU[i['ምግብ']] * i['ብዛት']})
        st.toast("✅ ተጨምሯል")
    else:
        st.warning("እባክዎ መጀመሪያ ምግብ ይምረጡ")

if st.session_state.cart:
    st.divider()
    total_bill = sum(item['ዋጋ'] for item in st.session_state.cart)
    summary = "\n".join([f"• {item['ዝርዝር']} [{item['ሁኔታ']}]" for item in st.session_state.cart])
    
    st.markdown(f"### ጠቅላላ: {total_bill:.2f} ብር")
    
    if st.button("ትዕዛዝ አስተላልፍ 🚀", use_container_width=True):
        if first_name:
            msg = f"🔔 <b>አዲስ ትዕዛዝ</b>\n👤 ደንበኛ: {first_name}\n📞 ስልክ: {c_tele}\n📝 ዝርዝር:\n{summary}\n💰 ጠቅላላ: {total_bill} ብር"
            send_telegram_msg(msg)
            st.session_state.last_order_sent = True
            st.session_state.order_status = "የምግብ ቤቱን ምላሽ በመጠባበቅ ላይ... ⏳"
            st.success("ትዕዛዝዎ ተልኳል! እባክዎ ምላሽ እስኪመጣ ድረስ ገጹን አይዝጉት።")
        else:
            st.warning("እባክዎ ስምዎን ያስገቡ")

# --- የሁኔታ መከታተያ (Status Checker) ---
if st.session_state.last_order_sent:
    st.markdown(f"""<div class='status-card'><h3>የትዕዛዝ ሁኔታ</h3><p>{st.session_state.order_status}</p></div>""", unsafe_allow_html=True)
    
    # ምላሽ እስኪመጣ በየጥቂት ሰከንዱ ይፈትሻል
    if "ተቀባይነት" not in st.session_state.order_status and "ይቅርታ" not in st.session_state.order_status:
        with st.spinner("ምላሽ በመጠበቅ ላይ..."):
            new_status = check_for_response()
            if new_status:
                st.session_state.order_status = new_status
                st.rerun()
            time.sleep(2) # ለ 2 ሰከንድ መጠበቅ

st.markdown(f"<p style='text-align:center; color:#718096; font-size:11px; margin-top:50px;'>Developer: <b>Belachew Damtie</b></p>", unsafe_allow_html=True)
