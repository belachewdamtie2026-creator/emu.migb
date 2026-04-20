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

# --- 2. የዳታ ቤዝ ተግባራት ---
def load_data(sheet_name):
    """ዳታ ከ Google Sheets ለማንበብ"""
    try:
        # ሺቱን ለማንበብ ይሞክራል
        df = conn.read(worksheet=sheet_name, ttl=0)
        return df
    except Exception as e:
        return pd.DataFrame()

def save_data(sheet_name, new_data_dict):
    """አዲስ ዳታ ወደ Google Sheets ለመጨመር"""
    try:
        # 1. ያለውን ዳታ ማንበብ
        existing_df = load_data(sheet_name)
        new_row = pd.DataFrame([new_data_dict])
        
        # 2. ዳታውን ማጣመር
        if not existing_df.empty:
            # Columns መመሳሰላቸውን ቼክ ያደርጋል
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
        else:
            updated_df = new_row
            
        # 3. ወደ ሺቱ መላክ
        conn.update(worksheet=sheet_name, data=updated_df)
        st.cache_data.clear() # አዲስ ዳታ እንዲታይ
        return True
    except Exception as e:
        st.error(f"መመዝገብ አልተቻለም (UnsupportedOperationError): {e}")
        st.info("ማሳሰቢያ፡ ሺቱ ላይ 'Share' ገብተው 'Anyone with the link' የሚለውን 'Editor' ማድረጎን ያረጋግጡ።")
        return False

# --- 3. UI እና ስታይል ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #f5f7f8; }
    .main-header { text-align: center; color: #FF5722; font-weight: bold; }
    .order-box {
        background-color: white; padding: 15px; border-radius: 12px;
        margin-bottom: 10px; border-left: 6px solid #FF5722;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

MENU = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

# --- Sidebar ---
st.sidebar.title("🍱 እሙ ምግብ ቤት")
app_url = "https://emumigb-2018.streamlit.app/" 
qr_img = qrcode.make(app_url)
buf = BytesIO()
qr_img.save(buf, format="PNG")
st.sidebar.image(buf.getvalue(), caption="በስልክዎ ስካን አድርገው ይዘዙ")

# --- Tabs ---
st.markdown("<h1 class='main-header'>🍳 እሙ ምግብ ቤት</h1>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🛍 ትዕዛዝ", "✍️ ፊርማ (ቋሚ)", "⚙️ አስተዳዳሪ"])

# --- Tab 1: Orders ---
with tab1:
    if 'cart' not in st.session_state: st.session_state.cart = []
    
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
        total_bill = 0
        summary = ""
        for i, item in enumerate(st.session_state.cart):
            st.markdown(f"<div class='order-box'><b>{item['ምግብ']}</b> (x{item['ብዛት']}) <span style='float:right;'>{item['ዋጋ']} ብር</span></div>", unsafe_allow_html=True)
            total_bill += item['ዋጋ']
            summary += f"{item['ምግብ']} (x{item['ብዛት']}), "
            if st.button(f"ሰርዝ", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
        
        st.markdown(f"<h2 style='text-align:right;'>ጠቅላላ: {total_bill} ብር</h2>", unsafe_allow_html=True)
        if st.button("ትዕዛዝ አስተላልፍ 🚀"):
            if c_name:
                # ወደ Orders ሉህ መመዝገብ
                success = save_data("Order", {"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Name": c_name, "Order": summary, "Total": total_bill})
                if success:
                    send_telegram_msg(f"🔔 <b>አዲስ ትዕዛዝ</b>\n👤 ስም: {c_name}\n📝 {summary}\n💰 <b>ጠቅላላ: {total_bill} ብር</b>")
                    st.success("ትዕዛዝዎ ደርሶናል!")
                    st.session_state.cart = []
                    st.balloons()
            else: st.warning("እባክዎ ስምዎን ያስገቡ")

# --- Tab 2: Signatures ---
with tab2:
    st.subheader("✍️ የቋሚ ተመጋቢዎች ፊርማ")
    users_df = load_data("Users")
    
    if not users_df.empty:
        selected_user = st.selectbox("ስምዎን ይምረጡ", ["ይምረጡ..."] + users_df['Name'].tolist())
        pin_input = st.text_input("PIN ቁጥር", type="password")
        eaten = st.multiselect("ዛሬ ምን ተመገቡ?", list(MENU.keys()))

        if st.button("አረጋግጣለሁ ✍️"):
            if selected_user != "ይምረጡ...":
                user_row = users_df[users_df['Name'] == selected_user]
                if pin_input == str(user_row['PIN'].values[0]):
                    if eaten:
                        price = sum(MENU[f] for f in eaten)
                        if save_data("Logs", {"Date": datetime.now().strftime("%Y-%m-%d"), "Name": selected_user, "Food": ", ".join(eaten), "Price": price}):
                            send_telegram_msg(f"✅ <b>ፊርማ</b>\n👤 {selected_user}\n🍲 {', '.join(eaten)}\n💰 {price} ብር")
                            st.success("በተሳካ ሁኔታ ተፈርሟል!")
                    else: st.error("ምግብ አልመረጡም")
                else: st.error("PIN ተሳስቷል")
    else:
        st.info("ምንም ደንበኛ አልተመዘገበም።")

# --- Tab 3: Admin ---
with tab3:
    if st.text_input("የባለቤት PIN", type="password") == ADMIN_PIN:
        st.markdown("#### ➕ አዲስ ደንበኛ መዝግብ")
        n_u = st.text_input("ስም")
        n_p = st.text_input("PIN")
        if st.button("መዝግብ"):
            if n_u and n_p:
                if save_data("Users", {"Name": n_u, "PIN": n_p}):
                    st.success("ተመዝግቧል!")
                    st.rerun()

        st.divider()
        st.markdown("#### 📜 የፊርማ ታሪክ")
        st.dataframe(load_data("Logs"), use_container_width=True)
