import streamlit as st
from datetime import datetime
import requests
import qrcode
from io import BytesIO
import urllib.parse

# --- 1. የቴሌግራም እና የደህንነት መረጃ ---
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
CHAT_ID = "1066005872"
OWNER_PHONE = "0919299256"
ADMIN_PIN = "admin123" 

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except:
        return False

# --- 2. ዳታ ቤዝ (Session State) ---
if 'cart' not in st.session_state: st.session_state.cart = []
if 'users_db' not in st.session_state:
    st.session_state.users_db = {"አህመድ መሀመድ": "1234", "ሳራ ካሳ": "5678"}
if 'logs' not in st.session_state: st.session_state.logs = []

menu = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

# --- 3. ገጽ ዝግጅት እና የውበት ስራ (CSS) ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

# እዚህ ጋር Background ቀለሙን ደብዘዝ ያለ ነጭ (#f5f7f8) አድርጌዋለሁ
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7f8; 
    }
    html, body, [class*="css"] {
        font-family: 'Nyala', 'Kefa', sans-serif;
    }
    .main-header {
        text-align: center;
        color: #FF5722;
        padding-bottom: 10px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    /* ሳጥኖች (Cards) ይበልጥ እንዲጎሉ */
    .order-box {
        border: none;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .stButton>button {
        border-radius: 25px;
        background-color: #FF5722;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #e64a19;
        transform: scale(1.02);
    }
    /* የTab ውበት */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar QR Code
app_url = "https://emumigb-2018.streamlit.app/" 
qr_img = qrcode.make(app_url)
buf = BytesIO()
qr_img.save(buf, format="PNG")
st.sidebar.title("🍱 እሙ ምግብ ቤት")
st.sidebar.image(buf.getvalue(), caption="ይህንን ስካን አድርገው ይዘዙ")
st.sidebar.write(f"📞 ባለቤት: **{OWNER_PHONE}**")

# የራስጌ ክፍል
st.markdown("<h1 class='main-header'>🍳 እሙ ምግብ ቤት</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555;'>እንኳን ደህና መጡ! የሚወዱትን ምግብ ይዘዙ ወይም ይፈሩሙ።</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛍 የእለቱ ትዕዛዝ", "✍️ የቋሚ ተመጋቢዎች ፊርማ", "⚙️ የባለቤት ክፍል"])

# --- Tab 1: የእለቱ ትዕዛዝ ---
with tab1:
    st.markdown("### 📝 አዲስ ትዕዛዝ")
    with st.container():
        col_n, col_t = st.columns(2)
        customer_name = col_n.text_input("👤 ስም", placeholder="ሙሉ ስም")
        telegram_username = col_t.text_input("💬 ቴሌግራም", placeholder="@username")
    
    selection_mode = st.radio("አቀራረብ", ["🍛 ለየብቻ", "🍱 በአንድ እቃ (Combo)"], horizontal=True)

    if selection_mode == "🍛 ለየብቻ":
        col1, col2 = st.columns([3, 1])
        food = col1.selectbox("ምግብ", list(menu.keys()), key="reg_food")
        qty = col2.number_input("ብዛት", min_value=1, value=1, key="reg_qty")
        if st.button("ወደ ቅርጫት ጨምር 🛒"):
            st.session_state.cart.append({"ምግብ": food, "ብዛት": qty, "ዋጋ": menu[food] * qty, "አቀራረብ": "ለየብቻ"})
            st.toast(f"✅ {food} ተጨምሯል!")

    else:
        selected_foods = st.multiselect("ምግቦችን ይምረጡ", list(menu.keys()), key="combo_select")
        if selected_foods:
            total_combo_price = 0
            combo_details = []
            for f in selected_foods:
                q = st.number_input(f"{f}", min_value=1, value=1, key=f"q_{f}")
                total_combo_price += menu[f] * q
                combo_details.append(f"{f}(x{q})")
            st.write(f"**ድምር: {total_combo_price:.2f} ብር**")
            if st.button("ጥምረቱን ወደ ቅርጫት ጨምር 🍱"):
                st.session_state.cart.append({"ምግብ": f"ጥምረት: {'+'.join(combo_details)}", "ብዛት": 1, "ዋጋ": total_combo_price, "አቀራረብ": "በአንድ እቃ"})
                st.rerun()

    if st.session_state.cart:
        st.divider()
        st.markdown("### 🛒 የያዙት ቅርጫት")
        total_bill = 0
        tg_summary = ""
        for i, item in enumerate(st.session_state.cart):
            with st.container():
                st.markdown(f"<div class='order-box'><b>{item['ምግብ']}</b> <span style='float:right; color:#FF5722;'>{item['ዋጋ']:.2f} ብር</span></div>", unsafe_allow_html=True)
                if st.button("ሰርዝ ❌", key=f"del_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
                total_bill += item["ዋጋ"]
                tg_summary += f"• {item['ምግብ']} - {item['ዋጋ']:.2f} ብር\n"

        st.markdown(f"<h3 style='text-align:right; color:#FF5722;'>💰 ጠቅላላ: {total_bill:.2f} ብር</h3>", unsafe_allow_html=True)
        if st.button("ትዕዛዝ አስተላልፍ 🚀"):
            if customer_name and telegram_username:
                order_id = datetime.now().strftime("%H%M%S")
                msg = f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n👤 ደንበኛ: {customer_name}\n📝 ዝርዝር:\n{tg_summary}\n💵 ጠቅላላ: {total_bill} ብር"
                if send_telegram_msg(msg):
                    st.success("✅ ትዕዛዝዎ ተልኳል!")
                    st.session_state.cart = []
                    st.balloons()
            else: st.error("ስም እና ቴሌግራም ያስገቡ!")

# --- Tab 2: የቋሚ ተመጋቢዎች ፊርማ ---
with tab2:
    st.markdown("### ✍️ የቋሚ ተመጋቢዎች ፊርማ")
    with st.container():
        selected_user = st.selectbox("👤 ስም", ["ስምዎን ይምረጡ..."] + list(st.session_state.users_db.keys()))
        user_pin = st.text_input("🔑 PIN", type="password")

    if selected_user != "ስምዎን ይምረጡ...":
        eaten_foods = st.multiselect("ዛሬ የተመገቡት", list(menu.keys()))
        if st.button("አረጋግጣለሁ (ፈርሜያለሁ) ✍️"):
            if user_pin == st.session_state.users_db[selected_user]:
                if eaten_foods:
                    total_p = sum(menu[f] for f in eaten_foods)
                    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    msg = f"<b>✅ አዲስ ፊርማ</b>\n👤 ደንበኛ: {selected_user}\n🍛 ምግቦች: {', '.join(eaten_foods)}\n💰 ሂሳብ: {total_p} ብር"
                    send_telegram_msg(msg)
                    st.session_state.logs.append({"ቀን": time_now, "ደንበኛ": selected_user, "ምግብ": ", ".join(eaten_foods), "ሂሳብ": total_p})
                    st.success("✅ በተሳካ ሁኔታ ተፈርሟል!")
                    st.balloons()
                else: st.error("ምግብ ይምረጡ!")
            else: st.error("PIN ተሳስቷል!")

# --- Tab 3: የባለቤት ክፍል ---
with tab3:
    st.markdown("### ⚙️ የአስተዳዳሪ ክፍል")
    admin_input = st.text_input("🔑 የባለቤት PIN", type="password")
    
    if admin_input == ADMIN_PIN:
        st.divider()
        st.markdown("#### ➕ አዲስ ደንበኛ")
        c1, c2, c3 = st.columns([3, 2, 1])
        u_name = c1.text_input("ስም", key="u_name")
        u_pin = c2.text_input("PIN", key="u_pin")
        if c3.button("መዝግብ"):
            if u_name and u_pin:
                st.session_state.users_db[u_name] = u_pin
                st.success("ተመዝግቧል!")
                st.rerun()

        st.divider()
        st.markdown("#### 👥 የተመዘገቡ ደንበኞች")
        for user, pin in st.session_state.users_db.items():
            with st.container():
                col_a, col_b, col_c = st.columns([4, 2, 1])
                col_a.write(f"👤 **{user}**")
                col_b.write(f"🔑 `{pin}`")
                if col_c.button("❌", key=f"rm_{user}"):
                    del st.session_state.users_db[user]
                    st.rerun()

        st.divider()
        st.markdown("#### 📜 ታሪክ")
        if st.session_state.logs:
            if st.button("ታሪክ አጽዳ"):
                st.session_state.logs = []
                st.rerun()
            st.table(st.session_state.logs)
    elif admin_input:
        st.error("PIN ተሳስቷል!")
