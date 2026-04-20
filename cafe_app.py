import streamlit as st
import pandas as pd
import requests
import qrcode
from io import BytesIO
from datetime import datetime
import random

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

# --- 2. የሚያምር ኢንተርፌስ (CSS) ---
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
    .receipt-box {
        border: 2px dashed #E64A19; padding: 20px; border-radius: 10px;
        background-color: #fff; font-family: monospace; line-height: 1.6;
    }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3em;
        background-color: #E64A19; color: white; border: none;
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
if 'receipt_data' not in st.session_state:
    st.session_state.receipt_data = None

col_a, col_b = st.columns(2)
first_name = col_a.text_input("👤 ስም", placeholder="የመጀመሪያ ስም")
username_input = col_b.text_input("💬 Telegram Username", placeholder="Username ያስገቡ")

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

if st.button("ወደ ቅርጫት ጨምር 🛒"):
    if food_items_to_add:
        if packing_style == "በአንድ እቃ":
            details = ", ".join([f"{i['ምግብ']} (x{i['ብዛት']})" for i in food_items_to_add])
            price = sum([MENU[i['ምግብ']] * i['ብዛት'] for i in food_items_to_add])
            st.session_state.cart.append({"ዝርዝር": details, "ሁኔታ": "በአንድ እቃ", "ዋጋ": price})
        else:
            for i in food_items_to_add:
                st.session_state.cart.append({"ዝርዝር": f"{i['ምግብ']} (x{i['ብዛት']})", "ሁኔታ": "ለየብቻ", "ዋጋ": MENU[i['ምግብ']] * i['ብዛት']})
        st.toast("✅ ተጨምሯል")
    else:
        st.warning("እባክዎ መጀመሪያ ምግብ ይምረጡ")

# --- የቅርጫት ዝርዝር እይታ ---
if st.session_state.cart:
    st.markdown("### 🛒 የእርስዎ ቅርጫት")
    total_bill = 0
    for i, item in enumerate(st.session_state.cart):
        col_item, col_del = st.columns([5, 1])
        with col_item:
            st.markdown(f"""<div class='order-box'><b>{item['ዝርዝር']}</b><br><small>ሁኔታ፦ {item['ሁኔታ']}</small><br><b style='color:#E64A19;'>{item['ዋጋ']:.2f} ብር</b></div>""", unsafe_allow_html=True)
        if col_del.button("❌", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()
        total_bill += item['ዋጋ']

    st.markdown(f"<h3 style='text-align:right;'>ጠቅላላ፦ {total_bill:.2f} ብር</h3>", unsafe_allow_html=True)
    
    if st.button("ትዕዛዝ አስተላልፍ 🚀"):
        if first_name and username_input:
            clean_username = username_input.replace("@", "").lower().strip()
            order_id = random.randint(1000, 9999)
            summary_text = "\n".join([f"• {item['ዝርዝር']} [{item['ሁኔታ']}]" for item in st.session_state.cart])
            
            accept_link = f"https://t.me/{clean_username}?text=ሰላም {first_name}፣ ትዕዛዝ #{order_id} ተቀብያለሁ። ✅"
            reject_link = f"https://t.me/{clean_username}?text=ይቅርታ {first_name}፣ ለትዕዛዝ #{order_id} ያዘዙት ምግብ አልቋል። ❌"
            
            owner_msg = (
                f"🔔 <b>አዲስ ትዕዛዝ #{order_id}</b>\n👤 ደንበኛ: {first_name}\n💬 Username: @{clean_username}\n"
                f"📝 ዝርዝር:\n{summary_text}\n💰 ጠቅላላ: <b>{total_bill:.2f} ብር</b>\n\n"
                f"✅ <a href='{accept_link}'>አለ ለማለት</a>\n❌ <a href='{reject_link}'>የለም ለማለት</a>"
            )
            
            send_to_owner(owner_msg)
            st.session_state.receipt_data = {
                "id": order_id, "name": first_name, "items": st.session_state.cart.copy(),
                "total": total_bill, "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.cart = []
            st.balloons()
            st.rerun()
        else:
            st.warning("እባክዎ ስምዎን እና Username ያስገቡ።")

# --- የረሲት እይታ ---
if st.session_state.receipt_data:
    st.divider()
    r = st.session_state.receipt_data
    st.markdown(f"""
    <div class='receipt-box'>
        <h3 style='text-align:center;'>እሙ ምግብ ቤት - ረሲት</h3>
        <hr>
        <p><b>ትዕዛዝ ቁጥር:</b> #{r['id']}</p>
        <p><b>ደንበኛ:</b> {r['name']}</p>
        <p><b>ቀን:</b> {r['time']}</p>
        <hr>
        {"".join([f"<p>{i['ዝርዝር']} - {i['ዋጋ']:.2f} ብር</p>" for i in r['items']])}
        <hr>
        <h4 style='text-align:right;'>ጠቅላላ: {r['total']:.2f} ብር</h4>
        <p style='text-align:center; font-size:12px;'>ስለመረጡን እናመሰግናለን!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("አዲስ ትዕዛዝ ጀምር"):
        st.session_state.receipt_data = None
        st.rerun()

st.markdown(f"<p style='text-align:center; color:#718096; font-size:11px; margin-top:50px;'>Developer: <b>Belachew Damtie</b></p>", unsafe_allow_html=True)
