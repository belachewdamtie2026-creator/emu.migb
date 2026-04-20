import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import requests

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
    .order-box {
        background-color: white; padding: 15px; border-radius: 12px;
        margin-bottom: 10px; border-left: 6px solid #E64A19;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
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
    st.divider()
    total_bill = sum(item['ዋጋ'] for item in st.session_state.cart)
    summary = "\n".join([f"• {item['ዝርዝር']} [{item['ሁኔታ']}]" for item in st.session_state.cart])
    
    if st.button("ትዕዛዝ አስተላልፍ 🚀", use_container_width=True):
        if first_name and username_input:
            clean_username = username_input.replace("@", "").lower().strip()
            
            # ደንበኛው ሊንኩን ተጭኖ እንዲያወራው ለባለቤቱ የሚላክ መልዕክት
            customer_link = f"https://t.me/{clean_username}"
            
            owner_msg = (
                f"🔔 <b>አዲስ ትዕዛዝ</b>\n"
                f"👤 ደንበኛ: {first_name}\n"
                f"💬 Username: @{clean_username}\n"
                f"🔗 ደንበኛውን ለማግኘት: <a href='{customer_link}'>እዚህ ይጫኑ</a>\n\n"
                f"📝 ዝርዝር:\n{summary}\n"
                f"💰 ጠቅላላ: <b>{total_bill:.2f} ብር</b>"
            )
            
            send_to_owner(owner_msg)
            st.success(f"እናመሰግናለን {first_name}! ትዕዛዝዎ ተልኳል። ባለቤቱ በቴሌግራምዎ ያገኝዎታል።")
            st.session_state.cart = []
            st.balloons()
        else:
            st.warning("እባክዎ ስምዎን እና ቴሌግራም ዩዘርኔምዎን ያስገቡ።")

st.markdown(f"<p style='text-align:center; color:#718096; font-size:11px; margin-top:50px;'>Developer: <b>Belachew Damtie</b></p>", unsafe_allow_html=True)
