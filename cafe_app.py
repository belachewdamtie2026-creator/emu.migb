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

# --- 2. ፕሪሚየም UI (Advanced CSS) ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

st.markdown("""
<style>
    /* አጠቃላይ የጀርባ ቀለም */
    .stApp {
        background: linear-gradient(135deg, #FFF5F0 0%, #FFEDD5 100%);
    }

    /* የርዕስ ክፍል አኒሜሽን */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #E64A19, #F57C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 5px;
        animation: fadeInDown 1s ease-out;
    }

    .sub-header {
        text-align: center;
        color: #5D4037;
        font-style: italic;
        margin-bottom: 30px;
    }

    /* የምግብ ካርዶች (Glassmorphism) */
    .order-box {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 8px 32px rgba(230, 74, 25, 0.1);
        transition: transform 0.3s ease;
    }
    
    .order-box:hover {
        transform: scale(1.02);
        border-left: 10px solid #E64A19;
    }

    /* የረሲት ስታይል */
    .receipt-box {
        background: white;
        padding: 30px;
        border-radius: 5px;
        box-shadow: 0 0 20px rgba(0,0,0,0.1);
        border-top: 10px solid #E64A19;
        font-family: 'Courier New', Courier, monospace;
        position: relative;
    }
    .receipt-box::after {
        content: "";
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 10px;
        background: linear-gradient(-45deg, transparent 5px, white 5px), linear-gradient(45deg, transparent 5px, white 5px);
        background-size: 10px 10px;
    }

    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(90deg, #E64A19, #FF7043);
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 50px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(230, 74, 25, 0.3);
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #BF360C, #E64A19);
        box-shadow: 0 6px 20px rgba(230, 74, 25, 0.5);
        transform: translateY(-2px);
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
st.markdown("<p class='sub-header'>ምርጥ የሀበሻ ቅምሻ በቤትዎ!</p>", unsafe_allow_html=True)

if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'receipt_data' not in st.session_state:
    st.session_state.receipt_data = None

# --- 4. የደንበኛ መረጃ ---
with st.expander("👤 የደንበኛ መረጃ መሙያ", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        first_name = st.text_input("የእርስዎ ስም", placeholder="ለምሳሌ፡ በላይነህ")
    with col_b:
        username_input = st.text_input("Telegram Username", placeholder="@username")

st.write("") # Space

# --- 5. ምግብ መምረጫ ---
st.markdown("### 🍽️ ትዕዛዝዎን ይምረጡ")
packing_style = st.radio("**የአቀራረብ ሁኔታ**", ["ለየብቻ", "በአንድ እቃ"], horizontal=True)

food_items_to_add = []
if packing_style == "በአንድ እቃ":
    selected_foods = st.multiselect("በአንድ እቃ የሚቀላቀሉ ምግቦችን ይምረጡ", list(MENU.keys()))
    if selected_foods:
        for f in selected_foods:
            c1, c2 = st.columns([3, 1])
            with c1: st.write(f"🔸 **{f}**")
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
            price = sum([MENU[i['ምግብ']] * i['бዛት'] for i in food_items_to_add])
            st.session_state.cart.append({"ዝርዝር": details, "ሁኔታ": "በአንድ እቃ", "ዋጋ": price})
        else:
            for i in food_items_to_add:
                st.session_state.cart.append({"ዝርዝር": f"{i['ምግብ']} (x{i['ብዛት']})", "ሁኔታ": "ለየብቻ", "ዋጋ": MENU[i['ምግብ']] * i['ብዛት']})
        st.toast("✅ ተጨምሯል!")
    else:
        st.warning("እባክዎ መጀመሪያ ምግብ ይምረጡ")

# --- 6. የቅርጫት ዝርዝር ---
if st.session_state.cart:
    st.markdown("---")
    st.markdown("### 🛒 የእርስዎ ቅርጫት")
    total_bill = 0
    for i, item in enumerate(st.session_state.cart):
        col_item, col_del = st.columns([5, 1])
        with col_item:
            st.markdown(f"""
            <div class='order-box'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div><b>{item['ዝርዝር']}</b><br><small>📦 {item['ሁኔታ']}</small></div>
                    <div style='color:#E64A19; font-weight:bold;'>{item['ዋጋ']:.2f} ብር</div>
                </div>
            </div>""", unsafe_allow_html=True)
        with col_del:
            st.write("")
            if st.button("❌", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
        total_bill += item['ዋጋ']

    st.markdown(f"<h2 style='text-align:right; color:#E64A19;'>ጠቅላላ፦ {total_bill:.2f} ብር</h2>", unsafe_allow_html=True)
    
    if st.button("ትዕዛዝ አስተላልፍ 🚀"):
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
            st.warning("እባክዎ ስምዎን እና Username ያስገቡ።")

# --- 7. የረሲት እይታ ---
if st.session_state.receipt_data:
    st.divider()
    r = st.session_state.receipt_data
    st.markdown(f"""
    <div class='receipt-box'>
        <h3 style='text-align:center;'>እሙ ምግብ ቤት - ረሲት</h3>
        <p style='text-align:center; font-size:10px;'>ቀን: {r['time']}</p>
        <hr style='border: 1px dashed #eee;'>
        <p><b>ትዕዛዝ ቁጥር:</b> #{r['id']}</p>
        <p><b>ደንበኛ:</b> {r['name']}</p>
        <hr style='border: 1px dashed #eee;'>
        {"".join([f"<div style='display:flex; justify-content:space-between; font-size:13px;'><span>{i['ዝርዝር']}</span><span>{i['ዋጋ']:.2f}</span></div>" for i in r['items']])}
        <hr style='border: 1px dashed #eee;'>
        <h4 style='text-align:right;'>ጠቅላላ: {r['total']:.2f} ብር</h4>
        <p style='text-align:center; font-size:12px; margin-top:20px;'>ስለመረጡን እናመሰግናለን!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("አዲስ ትዕዛዝ ጀምር"):
        st.session_state.receipt_data = None
        st.rerun()

# --- Footer ---
st.markdown(f"<div style='margin-top:50px; text-align:center; opacity:0.6; font-size:12px;'>Developer: Belachew Damtie | 2024</div>", unsafe_allow_html=True)
