import streamlit as st
import pandas as pd
import requests
import qrcode
from io import BytesIO

# --- 1. ኮንፊገሬሽን ---
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
OWNER_CHAT_ID = "1066005872"

def send_to_owner(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": OWNER_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass

# --- 2. UI ዝግጅት ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #fdfdfd; }
    .main-header { text-align: center; color: #E64A19; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

MENU = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

st.markdown("<h1 class='main-header'>🍳 እሙ ምግብ ቤት</h1>", unsafe_allow_html=True)

if 'cart' not in st.session_state:
    st.session_state.cart = []

col_a, col_b = st.columns(2)
first_name = col_a.text_input("👤 ስም", placeholder="የመጀመሪያ ስም")
username_input = col_b.text_input("💬 Telegram Username", placeholder="ያለ @ ምልክት")

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
            details = ", ".join([f"{i['ምግብ']} (x{i['ብዛት']})" for i in food_items_to_add])
            price = sum([MENU[i['ምግብ']] * i['ብዛት'] for i in food_items_to_add])
            st.session_state.cart.append({"ዝርዝር": details, "ሁኔታ": "በአንድ እቃ", "ዋጋ": price})
        else:
            for i in food_items_to_add:
                st.session_state.cart.append({"ዝርዝር": f"{i['ምግብ']} (x{i['ብዛት']})", "ሁኔታ": "ለየብቻ", "ዋጋ": MENU[i['ምግብ']] * i['ብዛት']})
        st.toast("✅ ተጨምሯል")

if st.session_state.cart:
    total_bill = sum(item['ዋጋ'] for item in st.session_state.cart)
    summary = "\n".join([f"• {item['ዝርዝር']} [{item['ሁኔታ']}]" for item in st.session_state.cart])
    
    if st.button("ትዕዛዝ አስተላልፍ 🚀", use_container_width=True):
        if first_name and username_input:
            clean_username = username_input.replace("@", "").lower().strip()
            
            # ባለቤቱ ምላሽ ለመስጠት የሚጠቀምባቸው ሊንኮች
            accept_link = f"https://t.me/{clean_username}?text=ሰላም {first_name}፣ ያዘዙት ምግብ አለ፤ እየተዘጋጀ ነው። ✅"
            reject_link = f"https://t.me/{clean_username}?text=ይቅርታ {first_name}፣ ያዘዙት ምግብ ለጊዜው አልቋል። ❌"
            
            owner_msg = (
                f"🔔 <b>አዲስ ትዕዛዝ</b>\n"
                f"👤 ደንበኛ: {first_name}\n"
                f"💬 Username: @{clean_username}\n\n"
                f"📝 ዝርዝር:\n{summary}\n"
                f"💰 ጠቅላላ: <b>{total_bill:.2f} ብር</b>\n\n"
                f"<b>ምላሽ ለመስጠት፦</b>\n"
                f"✅ <a href='{accept_link}'>አለ ለማለት</a>\n"
                f"❌ <a href='{reject_link}'>የለም ለማለት</a>"
            )
            
            send_to_owner(owner_msg)
            st.success(f"ትዕዛዝዎ ተልኳል! ባለቤቱ በቴሌግራምዎ ያገኝዎታል።")
            st.session_state.cart = []
        else:
            st.warning("እባክዎ ስምዎን እና ዩዘርኔምዎን ያስገቡ።")

st.markdown(f"<p style='text-align:center; color:#718096; font-size:11px; margin-top:50px;'>Developer: <b>Belachew Damtie</b></p>", unsafe_allow_html=True)
