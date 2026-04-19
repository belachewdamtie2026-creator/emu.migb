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
ADMIN_PIN = "admin123" # የባለቤቱ መግቢያ

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
    # ለሙከራ ጥቂት ደንበኞች
    st.session_state.users_db = {"አህመድ መሀመድ": "1234", "ሳራ ካሳ": "5678"}
if 'logs' not in st.session_state: st.session_state.logs = []

menu = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

# --- 3. ገጽ ዝግጅት እና የውበት ስራ (CSS) ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

# Custom CSS for Styling
st.markdown("""
<style>
    /* የዋናው ገጽ ጀርባ ቀለም */
    .stApp {
        background-color: #f9f9f9;
    }
    
    /* የአማርኛ ፊደላት ማስተካከያ */
    html, body, [class*="css"]  {
        font-family: 'Nyala', 'Kefa', sans-serif;
    }
    
    /* የራስጌ ክፍል (Header) */
    .main-header {
        text-align: center;
        color: #FF5722;
        padding-bottom: 20px;
    }
    
    /* የነጭ ሳጥኖች ንድፍ (Card style) */
    .css-1r6slb0, .stSection {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* የTabs ውበት */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
        gap: 5px;
        padding: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF5722;
        color: white;
    }
    
    /* የቁልፎች (Buttons) ውበት */
    .stButton>button {
        border-radius: 20px;
        background-color: #FF5722;
        color: white;
        border: none;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #E64A19;
        color: white;
    }
    
    /* የቅርጫት እና የመፈረሚያ ሳጥኖች */
    .order-box {
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        background-color: #fff;
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

# --- 4. ዋናው ገጽ የራስጌ ክፍል ---
# የምግብ ፎቶ (ከተቻለ የራስህን ፎቶ እዚህ ሊንክ ተካው)
st.image("https://img.freepik.com/premium-vector/restaurant-logo-design_23-2148498561.jpg?w=740", width=150)
st.markdown("<h1 class='main-header'>🍳 እሙ ምግብ ቤት</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666;'>እንኳን ደህና መጡ! የሚወዱትን ምግብ ይዘዙ ወይም ይፈሩሙ።</p>", unsafe_allow_html=True)
st.divider()

# ዋና ማውጫ (Tabs with Icons)
tab1, tab2, tab3 = st.tabs(["🛍 የእለቱ ትዕዛዝ", "✍️ የቋሚ ተመጋቢዎች ፊርማ", "⚙️ የባለቤት ክፍል"])

# --- Tab 1: የእለቱ ትዕዛዝ (Regular Order) ---
with tab1:
    st.markdown("### 📝 አዲስ ትዕዛዝ ይሙሉ")
    with st.container(): # White card background
        col_n, col_t = st.columns(2)
        customer_name = col_n.text_input("👤 የእርስዎ ስም", placeholder="ሙሉ ስም")
        telegram_username = col_t.text_input("💬 የቴሌግራም መለያ", placeholder="@username")
        
        st.markdown("**🍽 ምን አይነት አቀራረብ ይፈልጋሉ?**")
        selection_mode = st.radio("", ["🍛 ለየብቻ", "🍱 በአንድ እቃ (Combo)"], horizontal=True)

    st.markdown("### 🥘 ምግብ ይምረጡ")
    if selection_mode == "🍛 ለየብቻ":
        with st.container():
            col1, col2 = st.columns([3, 1])
            food = col1.selectbox("ምግብ", list(menu.keys()), key="reg_food")
            qty = col2.number_input("ብዛት", min_value=1, value=1, key="reg_qty")
            if st.button("ወደ ቅርጫት ጨምር 🛒", key="add_reg"):
                st.session_state.cart.append({"ምግብ": food, "ብዛት": qty, "ዋጋ": menu[food] * qty, "አቀራረብ": "ለየብቻ"})
                st.toast(f"✅ {food} ተጨምሯል!")

    else:
        with st.container():
            selected_foods = st.multiselect("የሚቀላቀሉ ምግቦችን ይምረጡ", list(menu.keys()), key="combo_select")
            if selected_foods:
                total_combo_price = 0
                combo_details = []
                st.markdown("<p style='color:#666; font-size:14px;'>ለእያንዳንዱ መጠን ያስገቡ፡</p>", unsafe_allow_html=True)
                for f in selected_foods:
                    q = st.number_input(f"{f}", min_value=1, value=1, key=f"q_{f}")
                    total_combo_price += menu[f] * q
                    combo_details.append(f"{f}(x{q})")
                
                st.markdown(f"<h4 style='text-align:right;'>የጥምረቱ ዋጋ: {total_combo_price:.2f} ብር</h4>", unsafe_allow_html=True)
                if st.button("ጥምረቱን ወደ ቅርጫት ጨምር 🍱", key="add_combo"):
                    st.session_state.cart.append({"ምግብ": f"ጥምረት: {'+'.join(combo_details)}", "ብዛት": 1, "ዋጋ": total_combo_price, "አቀራረብ": "በአንድ እቃ"})
                    st.rerun()

    # ቅርጫት ማሳያ
    if st.session_state.cart:
        st.divider()
        st.markdown("### 🛒 የያዙት ቅርጫት")
        total_bill = 0
        receipt_rows = ""
        tg_summary = ""
        
        for i, item in enumerate(st.session_state.cart):
            with st.container():
                st.markdown(f"""
                <div class='order-box'>
                    <span style='font-size:18px; font-weight:bold;'>{item['ምግብ']}</span><br>
                    <span style='color:#666;'>{item['አቀራረብ']}</span>
                    <span style='float:right; font-weight:bold; color:#FF5722;'>{item['ዋጋ']:.2f} ብር</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Delete button with unique key
                c1, c2, c3 = st.columns([6, 1, 1])
                if c3.button("❌", key=f"del_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
                    
                total_bill += item["ዋጋ"]
                receipt_rows += f"<tr><td>{item['ምግብ']}</td><td style='text-align:right;'>{item['ዋጋ']:.2f}</td></tr>"
                icon = "🍱" if item['አቀራረብ'] == "በአንድ እቃ" else "🍛"
                tg_summary += f"{icon} {item['ምግብ']} - {item['ዋጋ']:.2f} ብር\n"

        st.markdown(f"<h3 style='text-align:right; color:#FF5722;'>💰 ጠቅላላ: {total_bill:.2f} ብር</h3>", unsafe_allow_html=True)
        if st.button("ትዕዛዝ አስተላልፍ 🚀", key="submit_order"):
            if customer_name and telegram_username:
                order_id = datetime.now().strftime("%H%M%S")
                clean_un = telegram_username.replace("@", "")
                yes_url = f"https://t.me/{clean_un}?text=ትዕዛዝ #{order_id} ተቀብለናል"
                
                msg = f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n👤 ደንበኛ: {customer_name}\n📝 ዝርዝር:\n{tg_summary}\n💵 ጠቅላላ: {total_bill} ብር\n\n✅ <a href='{yes_url}'>አለ/ተቀብለናል</a>"
                if send_telegram_msg(msg):
                    st.success("✅ ትዕዛዝዎ በተሳካ ሁኔታ ተልኳል!")
                    st.session_state.cart = []
                    st.balloons()
            else: st.error("❌ እባክዎ ስም እና ቴሌግራም ያስገቡ!")

# --- Tab 2: የቋሚ ተመጋቢዎች ፊርማ (Digital Signature) ---
with tab2:
    st.markdown("### ✍️ የቋሚ ተመጋቢዎች መፈረሚያ")
    with st.container():
        user_names = ["ስምዎን ይምረጡ..."] + list(st.session_state.users_db.keys())
        selected_user = st.selectbox("👤 የእርስዎ ስም", user_names, key="user_select")
        user_pin = st.text_input("🔑 የይለፍ ቃል (PIN)", type="password", key="p_input")

    if selected_user != "ስምዎን ይምረጡ...":
        st.divider()
        st.markdown(f"### 🥗 ሰላም {selected_user}፣ ዛሬ ምን ተመገቡ?")
        with st.container():
            eaten_foods = st.multiselect("የተመገቧቸው ምግቦች", list(menu.keys()), key="eaten")
            
            if st.button("አረጋግጣለሁ (ፈርሜያለሁ) ✍️", key="sign_order"):
                if user_pin == st.session_state.users_db[selected_user]:
                    if eaten_foods:
                        total_p = sum(menu[f] for f in eaten_foods)
                        time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        # ለባለቤቱ መላክ
                        msg = f"<b>✅ አዲስ ፊርማ (ቋሚ ተመጋቢ)</b>\n👤 ደንበኛ: {selected_user}\n🍛 ምግቦች: {', '.join(eaten_foods)}\n💰 ሂሳብ: {total_p} ብር\n📅 ቀን: {time_now}"
                        send_telegram_msg(msg)
                        
                        # መዝገብ ላይ ማስፈር
                        st.session_state.logs.append({"ቀን": time_now, "ደንበኛ": selected_user, "ምግብ": ", ".join(eaten_foods), "ሂሳብ": total_p})
                        st.success("✅ በተሳካ ሁኔታ ተፈርሟል! እናመሰግናለን።")
                        st.balloons()
                    else: st.error("❌ እባክዎ ምግብ ይምረጡ!")
                else: st.error("❌ የይለፍ ቃል ተሳስቷል!")

# --- Tab 3: የባለቤት ክፍል (Admin Panel) ---
with tab3:
    st.markdown("### ⚙️ የአስተዳዳሪ መቆጣጠሪያ")
    with st.container():
        admin_input = st.text_input("🔑 የባለቤት PIN ያስገቡ", type="password", key="admin_pin_input")
    
    if admin_input == ADMIN_PIN:
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### ➕ አዲስ ቋሚ ደንበኛ መዝግብ")
            new_u = st.text_input("ሙሉ ስም", key="new_user_name")
            new_p = st.text_input("PIN (ሚስጥር ቁጥር)", key="new_user_pin")
            if st.button("መዝግብ 💾", key="register_user"):
                if new_u and new_p:
                    st.session_state.users_db[new_u] = new_p
                    st.success(f"✅ {new_u} ተመዝግቧል!")
                else: st.error("❌ መረጃው ሙሉ አይደለም!")
        
        with col_b:
            st.markdown("#### 📜 የዛሬ የፊርማ ታሪክ")
            if st.session_state.logs:
                st.dataframe(st.session_state.logs, use_container_width=True)
            else: st.info("እስካሁን ምንም ፊርማ የለም።")
    elif admin_input:
        st.error("❌ የባለቤት PIN ተሳስቷል!")
