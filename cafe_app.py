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

# --- 2. ማራኪ ኢንተርፌስ (CSS) ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍲")

st.markdown("""
<style>
    /* የገጹ ዳራ */
    .stApp { background-color: #fcfcfc; }
    
    /* የርዕስ ዲዛይን */
    .main-header { 
        text-align: center; 
        color: #E64A19; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 45px;
        margin-bottom: 0px;
    }
    
    /* የምግብ ካርዶች */
    .order-box {
        background-color: white; 
        padding: 18px; 
        border-radius: 15px;
        margin-bottom: 12px; 
        border-left: 8px solid #E64A19;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
    }
    
    /* የረሲት ዲዛይን */
    .receipt-box {
        border: 2px dashed #E64A19; 
        padding: 25px; 
        border-radius: 15px;
        background-color: #ffffff; 
        font-family: 'Courier New', Courier, monospace; 
        line-height: 1.6;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
    }
    
    /* የቁልፎች ዲዛይን */
    .stButton>button {
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em;
        background-color: #E64A19; 
        color: white; 
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #bf360c;
        box-shadow: 0 4px 12px rgba(230, 74, 25, 0.3);
    }
</style>
""", unsafe_allow_html=True)

MENU = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

# --- ገጽታ ---
st.markdown("<h1 class='main-header'>🍽️ እሙ ምግብ ቤት</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#7f8c8d;'>ትኩስ እና ጣፋጭ ምግቦችን ከእኛ ዘንድ ይዘዙ!</p>", unsafe_allow_html=True)

if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'receipt_data' not in st.session_state:
    st.session_state.receipt_data = None

# የተጠቃሚ መረጃ
with st.container():
    col_a, col_b = st.columns(2)
    first_name = col_a.text_input("👤 ስም", placeholder="የእርሶ ስም")
    username_input = col_b.text_input("💬 Telegram Username", placeholder="ያለ @ ምልክት ቢሆን ይመረጣል")

st.divider()

# የማዘዣ አማራጮች
st.subheader("🍱 ምርጫዎን ይግለጹ")
packing_style = st.radio("**የአቀራረብ ሁኔታ**", ["ለየብቻ", "በአንድ እቃ"], horizontal=True)

food_items_to_add = []
if packing_style == "በአንድ እቃ":
    selected_foods = st.multiselect("በአንድ እቃ የሚቀላቀሉ ምግቦችን ይምረጡ", list(MENU.keys()))
    if selected_foods:
        for f in selected_foods:
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f"**🔹 {f}**")
            qty = c2.number_input("ብዛት", 1, 10, 1, key=f"mixed_{f}", label_visibility="collapsed")
            food_items_to_add.append({"ምግብ": f, "ብዛት": qty})
else:
    col_f, col_q = st.columns([3, 1])
    f = col_f.selectbox("የሚፈልጉትን ምግብ ይምረጡ", list(MENU.keys()))
    qty = col_q.number_input("ብዛት", 1, 20, 1)
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
        st.toast("✅ ወደ ቅርጫት ተጨምሯል!")
    else:
        st.warning("እባክዎ መጀመሪያ ምግብ ይምረጡ")

# --- የቅርጫት ዝርዝር ---
if st.session_state.cart:
    st.markdown("---")
    st.markdown("### 🛒 የእርስዎ ቅርጫት")
    total_bill = 0
    for i, item in enumerate(st.session_state.cart):
        col_item, col_del = st.columns([5, 1])
        with col_item:
            st.markdown(f"""
                <div class='order-box'>
                    <div style='display:flex; justify-content:space-between;'>
                        <b>{item['ዝርዝር']}</b>
                        <b style='color:#E64A19;'>{item['ዋጋ']:.2f} ብር</b>
                    </div>
                    <small style='color:#7f8c8d;'>አቀራረብ፦ {item['ሁኔታ']}</small>
                </div>
            """, unsafe_allow_html=True)
        with col_del:
            st.write("") # Padding
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
        total_bill += item['ዋጋ']

    st.markdown(f"<h3 style='text-align:right; color:#E64A19;'>ጠቅላላ፦ {total_bill:.2f} ብር</h3>", unsafe_allow_html=True)
    
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
            st.error("እባክዎ ስምዎን እና ቴሌግራም ዩዘርኔምዎን በትክክል ያስገቡ።")

# --- ዲጂታል ረሲት ---
if st.session_state.receipt_data:
    st.divider()
    r = st.session_state.receipt_data
    st.markdown(f"""
    <div class='receipt-box'>
        <h2 style='text-align:center; color:#E64A19; margin-top:0;'>እሙ ምግብ ቤት</h2>
        <p style='text-align:center; font-size:12px; margin-bottom:10px;'>ዲጂታል ደረሰኝ</p>
        <hr style='border-top: 1px dashed #bbb;'>
        <p><b>ትዕዛዝ ቁጥር:</b> #{r['id']}</p>
        <p><b>ደንበኛ:</b> {r['name']}</p>
        <p><b>ቀን:</b> {r['time']}</p>
        <hr style='border-top: 1px solid #eee;'>
        {"".join([f"<div style='display:flex; justify-content:space-between;'><span>{i['ዝርዝር']}</span><b>{i['ዋጋ']:.2f} ETB</b></div>" for i in r['items']])}
        <hr style='border-top: 2px solid #E64A19;'>
        <div style='display:flex; justify-content:space-between; font-weight:bold; font-size:18px;'>
            <span>ጠቅላላ:</span><span>{r['total']:.2f} ETB</span>
        </div>
        <br>
        <p style='text-align:center; color:#7f8c8d; font-size:13px;'>ስለመረጡን እናመሰግናለን!<br>መልካም ምግብ!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("አዲስ ትዕዛዝ ጀምር"):
        st.session_state.receipt_data = None
        st.rerun()

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#bdc3c7; font-size:11px;'>Developed by <b>Belachew Damtie</b></p>", unsafe_allow_html=True)
