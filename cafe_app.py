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

# --- 3. ገጽ ዝግጅት ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

# Sidebar QR Code
app_url = "https://emumigb-2018.streamlit.app/" 
qr_img = qrcode.make(app_url)
buf = BytesIO()
qr_img.save(buf, format="PNG")
st.sidebar.title("🍱 እሙ ምግብ ቤት")
st.sidebar.image(buf.getvalue(), caption="ይህንን ስካን አድርገው ይዘዙ")
st.sidebar.write(f"📞 ባለቤት: {OWNER_PHONE}")

# ዋና ማውጫ (Tabs)
tab1, tab2, tab3 = st.tabs(["🛒 የእለቱ ትዕዛዝ", "✍️ የቋሚ ተመጋቢዎች ፊርማ", "⚙️ የባለቤት ክፍል"])

# --- 4. የእለቱ ትዕዛዝ (የድሮው ኮድህ) ---
with tab1:
    st.subheader("🍳 መደበኛ ትዕዛዝ")
    customer_name = st.text_input("የእርስዎ ስም", placeholder="ሙሉ ስምዎን ያስገቡ", key="reg_name")
    telegram_username = st.text_input("የቴሌግራም መለያ (Username)", placeholder="@example", key="reg_tg")
    
    selection_mode = st.radio("የአቀራረብ ምርጫ", ["ለየብቻ", "በአንድ እቃ (Combo)"], horizontal=True)

    if selection_mode == "ለየብቻ":
        col1, col2 = st.columns([3, 1])
        food = col1.selectbox("ምግብ ይምረጡ", list(menu.keys()), key="reg_food")
        qty = col2.number_input("ብዛት", min_value=1, value=1, key="reg_qty")
        if st.button("ወደ ቅርጫት ጨምር 🛒"):
            st.session_state.cart.append({"ምግብ": food, "ብዛት": qty, "ዋጋ": menu[food] * qty, "አቀራረብ": "ለየብቻ"})
            st.toast(f"{food} ተጨምሯል!")

    else:
        selected_foods = st.multiselect("ምግቦችን ይምረጡ", list(menu.keys()), key="combo_select")
        if selected_foods:
            total_combo_price = 0
            combo_details = []
            for f in selected_foods:
                q = st.number_input(f"{f} መጠን", min_value=1, value=1, key=f"q_{f}")
                total_combo_price += menu[f] * q
                combo_details.append(f"{f} (x{q})")
            if st.button("ጥምረቱን ወደ ቅርጫት ጨምር 🍱"):
                st.session_state.cart.append({"ምግብ": f"ጥምረት: {' + '.join(combo_details)}", "ብዛት": 1, "ዋጋ": total_combo_price, "አቀራረብ": "በአንድ እቃ"})
                st.rerun()

    # ቅርጫት ማሳያ
    if st.session_state.cart:
        st.divider()
        st.markdown("### 🛒 የያዙት ቅርጫት")
        total_bill = 0
        receipt_rows = ""
        tg_summary = ""
        for i, item in enumerate(st.session_state.cart):
            c1, c2, c3 = st.columns([4, 2, 1])
            c1.write(f"**{item['ምግብ']}**")
            c2.write(f"{item['ዋጋ']:.2f} ብር")
            if c3.button("❌", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
            total_bill += item["ዋጋ"]
            receipt_rows += f"<tr><td>{item['ምግብ']}</td><td style='text-align:right;'>{item['ዋጋ']:.2f}</td></tr>"
            tg_summary += f"• {item['ምግብ']} - {item['ዋጋ']:.2f} ብር\n"

        st.markdown(f"### 💰 ጠቅላላ: **{total_bill:.2f} ብር**")
        if st.button("ትዕዛዝ አስተላልፍ 🚀"):
            if customer_name and telegram_username:
                order_id = datetime.now().strftime("%H%M%S")
                clean_un = telegram_username.replace("@", "")
                yes_url = f"https://t.me/{clean_un}?text=ትዕዛዝ #{order_id} ተቀብለናል"
                
                msg = f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n👤 ደንበኛ: {customer_name}\n📝 ዝርዝር:\n{tg_summary}\n💵 ጠቅላላ: {total_bill} ብር\n\n✅ <a href='{yes_url}'>አለ/ተቀብለናል</a>"
                if send_telegram_msg(msg):
                    st.success("ትዕዛዝዎ ተልኳል!")
                    st.session_state.cart = []
                    st.balloons()
            else: st.error("ስም እና ቴሌግራም ያስገቡ!")

# --- 5. የቋሚ ተመጋቢዎች ፊርማ (Tab 2) ---
with tab2:
    st.subheader("✍️ የቋሚ ተመጋቢዎች ዲጂታል ፊርማ")
    user_names = ["ስምዎን ይምረጡ..."] + list(st.session_state.users_db.keys())
    selected_user = st.selectbox("የተመጋቢ ስም", user_names)
    user_pin = st.text_input("የይለፍ ቃል (PIN)", type="password", key="p_input")

    if selected_user != "ስምዎን ይምረጡ...":
        st.info(f"ሰላም {selected_user}፣ ዛሬ የተመገቡትን ይምረጡ")
        eaten_foods = st.multiselect("የተመገቧቸው ምግቦች", list(menu.keys()), key="eaten")
        
        if st.button("አረጋግጣለሁ (ፈርሜያለሁ) ✍️"):
            if user_pin == st.session_state.users_db[selected_user]:
                if eaten_foods:
                    total_p = sum(menu[f] for f in eaten_foods)
                    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    # ለባለቤቱ መላክ
                    msg = f"<b>✅ አዲስ ፊርማ (ቋሚ ተመጋቢ)</b>\n👤 ደንበኛ: {selected_user}\n🍛 ምግቦች: {', '.join(eaten_foods)}\n💰 ሂሳብ: {total_p} ብር\n📅 ቀን: {time_now}"
                    send_telegram_msg(msg)
                    
                    # መዝገብ ላይ ማስፈር
                    st.session_state.logs.append({"ቀን": time_now, "ደንበኛ": selected_user, "ምግብ": ", ".join(eaten_foods), "ሂሳብ": total_p})
                    st.success("በተሳካ ሁኔታ ተፈርሟል!")
                    st.balloons()
                else: st.error("ምግብ አልመረጡም!")
            else: st.error("የይለፍ ቃል ተሳስቷል!")

# --- 6. የባለቤት ክፍል (Tab 3) ---
with tab3:
    st.subheader("⚙️ የአስተዳዳሪ ክፍል")
    admin_input = st.text_input("የባለቤት PIN ያስገቡ", type="password")
    if admin_input == ADMIN_PIN:
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("➕ **አዲስ ቋሚ ደንበኛ መዝግብ**")
            new_u = st.text_input("ሙሉ ስም")
            new_p = st.text_input("PIN (ሚስጥር ቁጥር)")
            if st.button("መዝግብ"):
                if new_u and new_p:
                    st.session_state.users_db[new_u] = new_p
                    st.success(f"{new_u} ተመዝግቧል!")
        with col_b:
            st.write("📜 **የፊርማ ታሪክ**")
            if st.session_state.logs:
                st.dataframe(st.session_state.logs)
            else: st.write("ምንም ፊርማ የለም")
