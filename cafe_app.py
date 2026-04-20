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
    }
    .stRadio > div { flex-direction: row !important; gap: 20px; justify-content: center; }
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

# 1. የአቀራረብ ሁኔታ ምርጫ (ይህ መጀመሪያ እንዲታይ ተደርጓል)
packing_style = st.radio("**የአቀራረብ ሁኔታ ይምረጡ**", ["ለየብቻ", "በአንድ እቃ"], horizontal=True)

food_items_to_add = []

if packing_style == "በአንድ እቃ":
    # ብዙ እንዲመርጥ መፍቀድ
    selected_foods = st.multiselect("በአንድ እቃ የሚቀላቀሉ ምግቦችን ይምረጡ", list(MENU.keys()))
    if selected_foods:
        st.info("ለእያንዳንዱ ምግብ መጠን ያስገቡ")
        for f in selected_foods:
            c1, c2 = st.columns([3, 1])
            with c1: st.write(f"**{f}**")
            qty = c2.number_input("ብዛት", 1, 10, 1, key=f"mixed_{f}", label_visibility="collapsed")
            food_items_to_add.append({"ምግብ": f, "ብዛት": qty})
else:
    # አንድ ብቻ እንዲመርጥ መፍቀድ
    f = st.selectbox("የሚፈልጉትን ምግብ ይምረጡ", list(MENU.keys()))
    qty = st.number_input("ብዛት", 1, 20, 1)
    food_items_to_add.append({"ምግብ": f, "ብዛት": qty})

# ወደ ቅርጫት መጨመሪያ ቁልፍ
if st.button("ወደ ቅርጫት ጨምር 🛒", use_container_width=True):
    if food_items_to_add:
        if packing_style == "በአንድ እቃ":
            # እንደ አንድ ጥቅል መያዝ
            details = ", ".join([f"{i['ምግብ']} (x{i['ብዛት']})" for i in food_items_to_add])
            price = sum([MENU[i['ምግብ']] * i['ብዛት'] for i in food_items_to_add])
            st.session_state.cart.append({"ዝርዝር": details, "ሁኔታ": "በአንድ እቃ", "ዋጋ": price})
        else:
            # ለየብቻ መያዝ
            for i in food_items_to_add:
                st.session_state.cart.append({
                    "ዝርዝር": f"{i['ምግብ']} (x{i['ብዛት']})",
                    "ሁኔታ": "ለየብቻ",
                    "ዋጋ": MENU[i['ምግብ']] * i['ብዛት']
                })
        st.toast("✅ ተጨምሯል")
    else:
        st.warning("እባክዎ መጀመሪያ ምግብ ይምረጡ")

# የቅርጫት እይታ
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
                    <span style='font-size: 15px;'><b>{item['ዝርዝር']}</b></span><br>
                    <small style='color: #757575;'>ሁኔታ፦ {item['ሁኔታ']}</small>
                    <span style='float: right; color: #E64A19; font-weight: bold;'>{item['ዋጋ']:.2f} ብር</span>
                </div>
            """, unsafe_allow_html=True)
            if col_del.button("❌", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
        
        total_bill += item['ዋጋ']
        summary += f"• {item['ዝርዝር']} [{item['ሁኔታ']}] - {item['ዋጋ']} ብር\n"
    
    st.markdown(f"<h2 style='text-align:right; color:#E64A19;'>ጠቅላላ: {total_bill:.2f} ብር</h2>", unsafe_allow_html=True)
    
    if st.button("ትዕዛዝ አስተላልፍ 🚀", use_container_width=True):
        if first_name:
            msg = f"🔔 <b>አዲስ ትዕዛዝ</b>\n\n👤 <b>ደንበኛ:</b> {first_name}\n📞 <b>ስልክ:</b> {c_tele}\n\n📝 <b>ዝርዝር:</b>\n{summary}\n💰 <b>ጠቅላላ: {total_bill} ብር</b>"
            send_telegram_msg(msg)
            st.success(f"እናመሰግናለን {first_name}! ትዕዛዝዎ ተልኳል።")
            st.session_state.cart = []
            st.balloons()
        else:
            st.warning("እባክዎ ስምዎን ያስገቡ")

st.markdown(f"<p style='text-align:center; color:#718096; font-size:11px; margin-top:50px;'>Developed by <b>Belachew Damtie</b></p>", unsafe_allow_html=True)
