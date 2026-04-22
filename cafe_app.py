import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime
import random
import urllib.parse

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

# --- 2. ፕሪሚየም UI (Superior Visual Design) ---
st.set_page_config(page_title="እሙ ምግብ ቤት | Emu Restaurant", layout="centered", page_icon="🍳")

st.markdown("""
<style>
    /* አጠቃላይ የጀርባ እና የፎንት ሁኔታ */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    
    .stApp {
        background: linear-gradient(160deg, #FFF9F5 0%, #FFE4D6 100%);
        font-family: 'Poppins', sans-serif;
    }

    /* የርዕስ ክፍል አኒሜሽን */
    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #D35400, #F39C12);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 0px;
        animation: slideUpFade 0.8s ease-out;
    }

    .sub-header {
        text-align: center;
        color: #8D6E63;
        font-size: 1.2rem;
        letter-spacing: 1px;
        margin-bottom: 40px;
        animation: slideUpFade 1s ease-out;
    }

    /* የምግብ ካርዶች (Elegant Design) */
    .order-box {
        background: #ffffff;
        padding: 25px;
        border-radius: 24px;
        margin-bottom: 18px;
        border: none;
        box-shadow: 0 10px 25px rgba(211, 84, 0, 0.08);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .order-box:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(211, 84, 0, 0.15);
        border-left: 12px solid #D35400;
    }

    /* የረሲት ስታይል */
    .receipt-box {
        background: #fff;
        padding: 35px;
        border-radius: 4px;
        box-shadow: 0 0 30px rgba(0,0,0,0.05);
        border-top: 12px solid #D35400;
        font-family: 'Courier New', Courier, monospace;
        position: relative;
    }

    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(90deg, #D35400, #E67E22);
        color: white;
        border: none;
        padding: 18px 25px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 1.1rem;
        width: 100%;
        transition: 0.4s;
        box-shadow: 0 8px 20px rgba(211, 84, 0, 0.25);
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #A04000, #D35400);
        box-shadow: 0 12px 25px rgba(211, 84, 0, 0.4);
        transform: scale(1.02);
        color: #fff;
    }
    
    /* Input Fields Design */
    .stTextInput>div>div>input {
        border-radius: 12px;
        border: 2px solid #FFE0D1;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ዳታ እና ዝርዝሮች ---
MENU = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

st.markdown("<h1 class='main-header'>🍳 እሙ ምግብ ቤት</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>በቤትዎ ሆነው ይዘዙ! • Fresh & Fast</p>", unsafe_allow_html=True)

if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'receipt_data' not in st.session_state:
    st.session_state.receipt_data = None

# --- 4. የደንበኛ መረጃ ---
with st.container():
    col_a, col_b = st.columns(2)
    with col_a:
        first_name = st.text_input("👤 ስምዎን ያስገቡ")
    with col_b:
        username_input = st.text_input("💬 ቴሌግራም", placeholder="@username")

st.markdown("---")

# --- 5. ምግብ መምረጫ ---
st.markdown("### 🍽️ ምግቦች")
packing_style = st.radio("**አቀራረብ**", ["ለየብቻ", "በአንድ እቃ"], horizontal=True)

food_items_to_add = []
if packing_style == "በአንድ እቃ":
    selected_foods = st.multiselect("በአንድ እቃ የሚቀላቀሉ ምግቦችን ይምረጡ", list(MENU.keys()))
    if selected_foods:
        for f in selected_foods:
            c1, c2 = st.columns([3, 1])
            with c1: st.write(f"✨ **{f}**")
            qty = c2.number_input("ብዛት", 1, 10, 1, key=f"mixed_{f}")
            food_items_to_add.append({"ምግብ": f, "ብዛት": qty})
else:
    f = st.selectbox("የሚፈልጉትን ምግብ ይምረጡ", list(MENU.keys()))
    qty = st.number_input("ብዛት", 1, 20, 1)
    food_items_to_add.append({"ምግብ": f, "ብዛት": qty})

st.write("")
if st.button("ወደ ቅርጫት ጨምር 🛒"):
    if food_items_to_add:
        if packing_style == "በአንድ እቃ":
            details = ", ".join([f"{i['ምግብ']} (x{i['ብዛት']})" for i in food_items_to_add])
            price = sum([MENU[i['ምግብ']] * i['бዛት'] for i in food_items_to_add])
            st.session_state.cart.append({"ዝርዝር": details, "ሁኔታ": "በአንድ እቃ", "ዋጋ": price})
        else:
            for i in food_items_to_add:
                st.session_state.cart.append({"ዝርዝር": f"{i['ምግብ']} (x{i['ብዛት']})", "ሁኔታ": "ለየብቻ", "ዋጋ": MENU[i['ምግብ']] * i['ብዛት']})
        st.toast("✅ በተሳካ ሁኔታ ተጨምሯል!")
    else:
        st.warning("እባክዎ መጀመሪያ ምግብ ይምረጡ")

# --- 6. የቅርጫት ዝርዝር ---
if st.session_state.cart:
    st.markdown("---")
    st.markdown("### 🛒 ያዘዟቸው ምግቦች")
    total_bill = 0
    for i, item in enumerate(st.session_state.cart):
        col_item, col_del = st.columns([5, 1])
        with col_item:
            st.markdown(f"""
            <div class='order-box'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div><b style='font-size:1.2rem; color:#4E342E;'>{item['ዝርዝር']}</b><br>
                    <span style='color:#A1887F;'>📦 አቀራረብ፦ {item['ሁኔታ']}</span></div>
                    <div style='color:#D35400; font-weight:800; font-size:1.3rem;'>{item['ዋጋ']:.2f} ብር</div>
                </div>
            </div>""", unsafe_allow_html=True)
        with col_del:
            st.write(" ")
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
        total_bill += item['ዋጋ']

    st.markdown(f"<h2 style='text-align:right; color:#D35400; padding-top:20px;'>ጠቅላላ፦ {total_bill:.2f} ብር</h2>", unsafe_allow_html=True)
    
    if st.button("ትዕዛዝ አስተላልፍ (Order Now) 🚀"):
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
            st.warning("እባክዎ ስምዎን እና ቴሌግራምዎን ያስገቡ።")

# --- 7. የረሲት እይታ ---
if st.session_state.receipt_data:
    st.divider()
    r = st.session_state.receipt_data
    st.markdown(f"""
    <div class='receipt-box'>
        <h2 style='text-align:center; color:#333;'>EMU RESTAURANT</h2>
        <p style='text-align:center; font-size:12px; color:#777;'>ቀን: {r['time']}</p>
        <div style='border-top: 2px dashed #DDD; margin: 20px 0;'></div>
        <p><b>RECEIPT ID:</b> #{r['id']}</p>
        <p><b>CUSTOMER:</b> {r['name']}</p>
        <div style='border-top: 1px solid #EEE; margin: 15px 0;'></div>
        {"".join([f"<div style='display:flex; justify-content:space-between; margin-bottom:8px;'><span>{i['ዝርዝር']}</span><b>{i['ዋጋ']:.2f}</b></div>" for i in r['items']])}
        <div style='border-top: 2px dashed #DDD; margin: 20px 0;'></div>
        <h3 style='text-align:right; color:#D35400;'>TOTAL: {r['total']:.2f} ETB</h3>
        <p style='text-align:center; font-size:14px; margin-top:30px; color:#888;'>በመረጡን እናመሰግናለን!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("ተጨማሪ እዘዝ ✨"):
        st.session_state.receipt_data = None
        st.rerun()

# --- Footer ---
st.markdown(f"<div style='margin-top:60px; text-align:center; opacity:0.5; font-size:13px; color:#5D4037;'>Crafted for Emu Restaurant by <b>Belachew Damtie</b> | 2026</div>", unsafe_allow_html=True)
