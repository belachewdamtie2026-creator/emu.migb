import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests
import qrcode
from io import BytesIO

# --- 1. ኮንፊገሬሽን (Telegram & Admin) ---
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
CHAT_ID = "1066005872"
ADMIN_PIN = "admin123"

# Google Sheets ግንኙነት መፍጠር
conn = st.connection("gsheets", type=GSheetsConnection)

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=5)
    except:
        pass

# --- 2. የዳታ ቤዝ ተግባራት (CRUD) ---
def load_data(sheet_name):
    """ዳታ ከ Google Sheets ለማንበብ"""
    try:
        return conn.read(worksheet=sheet_name, ttl=0)
    except Exception:
        return pd.DataFrame()

def save_data(sheet_name, new_data_dict):
    """አዲስ ዳታ ወደ Google Sheets ለመጨመር"""
    existing_df = load_data(sheet_name)
    new_row = pd.DataFrame([new_data_dict])
    # ዳታውን ማጣመር
    if not existing_df.empty:
        updated_df = pd.concat([existing_df, new_row], ignore_index=True)
    else:
        updated_df = new_row
    # ወደ ሺቱ መላክ
    conn.update(worksheet=sheet_name, data=updated_df)
    st.cache_data.clear() # ዳታው ወዲያው እንዲታይ ካሹን ማጽዳት

# --- 3. ገጽ ዝግጅት እና ስታይል ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #f5f7f8; }
    .main-header { text-align: center; color: #FF5722; font-weight: bold; margin-bottom: 0px; }
    .order-box {
        background-color: white; padding: 15px; border-radius: 12px;
        margin-bottom: 10px; border-left: 6px solid #FF5722;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .stButton>button { border-radius: 20px; width: 100%; }
</style>
""", unsafe_allow_html=True)

MENU = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

# --- Sidebar (QR Code) ---
st.sidebar.title("🍱 እሙ ምግብ ቤት")
app_url = "https://emumigb-2018.streamlit.app/" 
qr_img = qrcode.make(app_url)
buf = BytesIO()
qr_img.save(buf, format="PNG")
st.sidebar.image(buf.getvalue(), caption="በስልኮ ይዘዙ")

# --- ዋናው ክፍል ---
st.markdown("<h1 class='main-header'>🍳 እሙ ምግብ ቤት</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>እንኳን ደህና መጡ! ትኩስ እና ጣፋጭ ምግቦች።</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛍 ትዕዛዝ", "✍️ ፊርማ (ቋሚ)", "⚙️ አስተዳዳሪ"])

# --- Tab 1: የእለቱ ትዕዛዝ ---
with tab1:
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    with st.container():
        col_a, col_b = st.columns(2)
        c_name = col_a.text_input("👤 ስም")
        c_tele = col_b.text_input("💬 ቴሌግራም")

    col_f, col_q = st.columns([3, 1])
    food = col_f.selectbox("ምግብ ይምረጡ", list(MENU.keys()))
    qty = col_q.number_input("ብዛት", 1, 20, 1)

    if st.button("ወደ ቅርጫት ጨምር 🛒"):
        st.session_state.cart.append({"ምግብ": food, "ብዛት": qty, "ዋጋ": MENU[food]*qty})
        st.toast(f"✅ {food} ተጨምሯል")

    if st.session_state.cart:
        st.divider()
        st.markdown("### 🛒 የያዙት ምግቦች")
        total_bill = 0
        summary_txt = ""
        for i, item in enumerate(st.session_state.cart):
            st.markdown(f"<div class='order-box'><b>{item['ምግብ']}</b> (x{item['ብዛት']}) <span style='float:right;'>{item['ዋጋ']} ብር</span></div>", unsafe_allow_html=True)
            total_bill += item['ዋጋ']
            summary_txt += f"• {item['ምግብ']} (x{item['ብዛት']})\n"
            if st.button(f"ሰርዝ", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
        
        st.markdown(f"<h2 style='text-align:right; color:#FF5722;'>ጠቅላላ: {total_bill} ብር</h2>", unsafe_allow_html=True)
        if st.button("ትዕዛዝ አስተላልፍ 🚀"):
            if c_name:
                # 1. ወደ GSheets መመዝገብ
                save_data("Orders", {"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Name": c_name, "Order": summary_txt.replace('\n', ' '), "Total": total_bill})
                # 2. ወደ Telegram መላክ
                msg = f"<b>🔔 አዲስ ትዕዛዝ</b>\n👤 ደንበኛ: {c_name}\n📝 ዝርዝር:\n{summary_txt}💰 <b>ጠቅላላ: {total_bill} ብር</b>"
                send_telegram_msg(msg)
                
                st.success("ትዕዛዝዎ በተሳካ ሁኔታ ደርሶናል!")
                st.session_state.cart = []
                st.balloons()
            else: st.warning("እባክዎ ስምዎን ያስገቡ!")

# --- Tab 2: የቋሚ ተመጋቢዎች ፊርማ ---
with tab2:
    st.subheader("✍️ የቋሚ ተመጋቢዎች ፊርማ")
    users_df = load_data("Users")
    
    if not users_df.empty:
        selected_user = st.selectbox("ስምዎን ይምረጡ", ["ይምረጡ..."] + users_df['Name'].tolist())
        pin_input = st.text_input("የእርስዎ PIN", type="password")
        eaten = st.multiselect("የተመገቡት ምግብ", list(MENU.keys()))

        if st.button("አረጋግጣለሁ (ፈርሜያለሁ) ✍️"):
            if selected_user != "ይምረጡ...":
                user_info = users_df[users_df['Name'] == selected_user]
                correct_pin = str(user_info['PIN'].values[0])
                if pin_input == correct_pin:
                    if eaten:
                        total_p = sum(MENU[f] for f in eaten)
                        # ወደ GSheets መመዝገብ
                        save_data("Logs", {"Date": datetime.now().strftime("%Y-%m-%d"), "Name": selected_user, "Food": ", ".join(eaten), "Price": total_p})
                        # ወደ Telegram መላክ
                        send_telegram_msg(f"✅ <b>ፊርማ</b>\n👤 {selected_user}\n🍲 {', '.join(eaten)}\n💵 <b>{total_p} ብር</b>")
                        st.success(f"ተመዝግቧል! {total_p} ብር በሂሳብዎ ተይዟል።")
                    else: st.error("ምግብ አልመረጡም!")
                else: st.error("PIN ተሳስቷል!")
            else: st.warning("ስም ይምረጡ")
    else:
        st.info("ምንም የተመዘገበ ደንበኛ የለም።")

# --- Tab 3: የአስተዳዳሪ ክፍል ---
with tab3:
    admin_pin = st.text_input("የባለቤት PIN", type="password")
    if admin_pin == ADMIN_PIN:
        st.markdown("#### 👤 አዲስ ቋሚ ደንበኛ መመዝገቢያ")
        new_name = st.text_input("የደንበኛ ስም")
        new_pin = st.text_input("የደንበኛ PIN")
        if st.button("ደንበኛ መዝግብ"):
            if new_name and new_pin:
                save_data("Users", {"Name": new_name, "PIN": new_pin})
                st.success(f"{new_name} በተሳካ ሁኔታ ተመዝግቧል!")
                st.rerun()

        st.divider()
        st.markdown("#### 📜 የፊርማ ታሪክ (Logs)")
        logs_df = load_data("Logs")
        if not logs_df.empty:
            st.dataframe(logs_df, use_container_width=True)
        else:
            st.write("ምንም የታሪክ መዝገብ የለም።")
    elif admin_pin:
        st.error("PIN ተሳስቷል!")
