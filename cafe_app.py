import streamlit as st
import pandas as pd
import requests
import qrcode
from io import BytesIO
from datetime import datetime
import random
import urllib.parse

# --- 1. ኮንፊገሬሽን (እንደነበረው) ---
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
OWNER_CHAT_ID = "1066005872"

def send_to_owner(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": OWNER_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass

# --- 2. ፕሪሚየም ኢንተርፌስ (CSS Customization) ---
st.set_page_config(page_title="እሙ ምግብ ቤት | Emu Restaurant", layout="centered", page_icon="🍳")

st.markdown("""
<style>
    /* አጠቃላይ ገጽታ */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Ethiopic:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans Ethiopic', sans-serif;
    }

    .stApp {
        background: linear-gradient(to bottom, #fffcf9, #f7f7f7);
    }

    /* የርዕስ ክፍል */
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .sub-header {
        text-align: center;
        color: #555;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    /* የካርድ ዲዛይን (Card Style) */
    .order-box {
        background-color: white;
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 15px;
        border: 1px solid #eee;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
    }
    
    .order-box:hover {
        transform: translateY(-5px);
        border-left: 8px solid #FF416C;
    }

    /* የረሲት ዲዛይን */
    .receipt-box {
        border: 3px solid #333;
        padding: 25px;
        border-radius: 0px;
        background-color: #fff;
        font-family: 'Courier New', Courier, monospace;
        box-shadow: 10px 10px 0px #FF416C;
        color: #333;
    }

    /* Buttons Style */
    div.stButton > button {
        background: linear-gradient(90deg, #FF4B2B, #FF416C);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 75, 43, 0.3);
    }

    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(255, 75, 43, 0.4);
        color: white;
    }

    /* Input Fields */
    .stTextInput input, .stSelectbox select {
        border-radius: 10px !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #888;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ዳታ እና ዝርዝሮች ---
MENU = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

# ርዕስ
st.markdown("<h1 class='main-header'>🍳 እሙ ምግብ ቤት</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>ምርጥ የሀበሻ ምግቦች በአጭር ጊዜ ከእጅዎ!</p>", unsafe_allow_html=True)

if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'receipt_data' not in st.session_state:
    st.session_state.receipt_data = None

# --- 4. የደንበኛ መረጃ ---
with st.container():
    st.markdown("### 👤 የደንበኛ መረጃ")
    col_a, col_b = st.columns(2)
    with col_a:
        first_name = st.text_input("ስም", placeholder="የመጀመሪያ ስምዎን ያስገቡ")
    with col_b:
        username_input = st.text_input("Telegram Username", placeholder="@username")

st.divider()

# --- 5. ምግብ መምረጫ ---
with st.container():
    st.markdown("### 🍽️ ምግብ ይምረጡ")
    packing_style = st.radio("**የአቀራረብ ሁኔታ**", ["ለየብቻ", "በአንድ እቃ"], horizontal=True)

    food_items_to_add = []
    if packing_style == "በአንድ እቃ":
        selected_foods = st.multiselect("በአንድ እቃ የሚቀላቀሉ ምግቦችን ይምረጡ", list(MENU.keys()))
        if selected_foods:
            for f in selected_foods:
                c1, c2 = st.columns([3, 1])
                with c1: st.write(f"**{f}**")
                qty = c2.number_input("ብዛት", 1, 10, 1, key=f"mixed_{f}")
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
            st.toast("✅ ምግብ ተጨምሯል!", icon='🔥')
        else:
            st.warning("እባክዎ መጀመሪያ ምግብ ይምረጡ")

# --- 6. የቅርጫት ዝርዝር ---
if st.session_state.cart:
    st.markdown("---")
    st.markdown("### 🛒 ያዘዟቸው ምግቦች")
    total_bill = 0
    
    for i, item in enumerate(st.session_state.cart):
        col_item, col_del = st.columns([6, 1])
        with col_item:
            st.markdown(f"""
            <div class='order-box'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='font-size: 1.2rem; font-weight: bold; color: #333;'>{item['ዝርዝር']}</span><br>
                        <small style='color: #888;'>አቀራረብ፦ {item['ሁኔታ']}</small>
                    </div>
                    <div style='font-weight: 800; color: #FF416C; font-size: 1.2rem;'>{item['ዋጋ']:.2f} ብር</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_del:
            st.write("") # ለስፔስ
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
        total_bill += item['ዋጋ']

    st.markdown(f"""
        <div style='text-align: right; padding: 20px; background: #eee; border-radius: 10px;'>
            <span style='font-size: 1.5rem;'>ጠቅላላ ድምር፦ </span>
            <span style='font-size: 2rem; font-weight: bold; color: #FF416C;'>{total_bill:.2f} ብር</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("ትዕዛዝ አሁን አስተላልፍ 🚀"):
        if first_name and username_input:
            clean_username = username_input.replace("@", "").lower().strip()
            order_id = random.randint(1000, 9999)
            summary_text = "\n".join([f"• {item['ዝርዝር']} [{item['ሁኔታ']}]" for item in st.session_state.cart])
            
            accept_text = urllib.parse.quote(f"ሰላም {first_name}፣ ትዕዛዝ #{order_id} ተቀብያለሁ፤ እየተዘጋጀ ነው። ✅")
            reject_text = urllib.parse.quote(f"ይቅርታ {first_name}፣ ለትዕዛዝ #{order_id} ያዘዙት ምግብ ለጊዜው አልቋል። ❌")
            
            accept_link = f"https://t.me/{clean_username}?text={accept_text}"
            reject_link = f"https://t.me/{clean_username}?text={reject_text}"
            
            owner_msg = (
                f"🔔 <b>አዲስ ትዕዛዝ #{order_id}</b>\n"
                f"👤 ደንበኛ: {first_name}\n"
                f"💬 Username: @{clean_username}\n\n"
                f"📝 ዝርዝር:\n{summary_text}\n"
                f"💰 ጠቅላላ: <b>{total_bill:.2f} ብር</b>\n\n"
                f"<b>ምላሽ ለመስጠት፦</b>\n"
                f"✅ <a href='{accept_link}'>አለ ለማለት</a>\n"
                f"❌ <a href='{reject_link}'>የለም ለማለት</a>"
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
            st.warning("እባክዎ መጀመሪያ ስምዎን እና ቴሌግራምዎን ያስገቡ።")

# --- 7. የረሲት እይታ ---
if st.session_state.receipt_data:
    st.divider()
    r = st.session_state.receipt_data
    
    st.markdown(f"""
    <div class='receipt-box'>
        <h2 style='text-align:center; margin-bottom: 5px;'>እሙ ምግብ ቤት</h2>
        <p style='text-align:center; font-size: 12px; margin-top: 0;'>ቅምሻዎ በእኛ ይታደሳል!</p>
        <div style='border-top: 2px dashed #333; margin: 15px 0;'></div>
        <p><b>ትዕዛዝ ቁጥር:</b> #{r['id']}</p>
        <p><b>ደንበኛ:</b> {r['name']}</p>
        <p><b>ቀን:</b> {r['time']}</p>
        <div style='border-top: 1px solid #eee; margin: 10px 0;'></div>
        {"".join([f"<div style='display:flex; justify-content:space-between;'><span>{i['ዝርዝር']}</span> <span>{i['ዋጋ']:.2f}</span></div>" for i in r['items']])}
        <div style='border-top: 2px dashed #333; margin: 15px 0;'></div>
        <div style='display:flex; justify-content:space-between; font-weight:bold; font-size: 1.2rem;'>
            <span>ጠቅላላ:</span> <span>{r['total']:.2f} ብር</span>
        </div>
        <br>
        <p style='text-align:center; font-style: italic;'>ስለመረጡን እናመሰግናለን!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("አዲስ ትዕዛዝ ጀምር ✨"):
        st.session_state.receipt_data = None
        st.rerun()

# --- Footer ---
st.markdown(f"""
<div class='footer'>
    <hr>
    Developed by <b>Belachew Damtie</b><br>
    © {datetime.now().year} Emu Restaurant Delivery
</div>
""", unsafe_allow_html=True)
