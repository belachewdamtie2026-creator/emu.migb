import streamlit as st
from datetime import datetime
import requests
import qrcode
from io import BytesIO
import urllib.parse

# --- 1. የቴሌግራም መረጃ ---
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
CHAT_ID = "1066005872"
OWNER_PHONE = "0919299256"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except:
        return False

# --- 2. የገጽ ዝግጅት ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

menu = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

# --- 3. Sidebar (QR Code) ---
app_url = "https://emumigb2018.streamlit.app/" 
qr_img = qrcode.make(app_url)
buf = BytesIO()
qr_img.save(buf, format="PNG")

st.sidebar.title("🍱 እሙ ምግብ ቤት")
st.sidebar.write(f"📞 ባለቤት: {OWNER_PHONE}")
st.sidebar.image(buf.getvalue(), caption="ይህንን ስካን አድርገው ይዘዙ")

# --- 4. ዋናው ገጽ ---
st.title("🍳 እሙ ምግብ ቤት")

customer_name = st.text_input("የእርስዎ ስም")
telegram_username = st.text_input("የቴሌግራም መለያ (Username)", placeholder="@example")
food = st.selectbox("ምን መመገብ ይፈልጋሉ?", list(menu.keys()))

unit_price = menu[food]
qty = st.number_input("ብዛት", min_value=1, value=1, step=1)
total_bill = unit_price * qty

if st.button("ትዕዛዝ አስተላልፍ 🚀"):
    if customer_name and telegram_username:
        clean_username = telegram_username.replace("@", "").strip()
        
        # የመልዕክት ቅጽ (Templates) ለባለቤቱ እንዲቀልላቸው
        yes_msg = urllib.parse.quote(f"ሰላም {customer_name}፣ ደርሶናል እናመሰግናለን! ትዕዛዝዎን እያዘጋጀን ነው።")
        no_msg = urllib.parse.quote(f"ይቅርታ {customer_name}፣ ለጊዜው {food} የለም፤ እባክዎ ሌላ ይዘዙ።")
        
        # የቴሌግራም ሊንኮች ከመልዕክት ጋር
        confirm_link = f"https://t.me/{clean_username}?text={yes_msg}"
        reject_link = f"https://t.me/{clean_username}?text={no_msg}"
        
        now = datetime.now().strftime("%I:%M %p")
        
        # ባለቤቱ ጋር የሚሄደው መልዕክት
        owner_msg = (
            f"<b>🔔 አዲስ ትዕዛዝ ደርሷል!</b>\n\n"
            f"👤 <b>ደንበኛ:</b> {customer_name}\n"
            f"🍲 <b>ምግብ:</b> {food} ({qty})\n"
            f"💵 <b>ሂሳብ:</b> {total_bill} ብር\n"
            f"🕒 <b>ሰዓት:</b> {now}\n\n"
            f"👇 <b>አማራጮች (ሲጫኑት መልዕክቱ ተጽፎ ይጠብቅዎታል)፦</b>\n\n"
            f"✅ <a href='{confirm_link}'>ደርሶናል ለማለት እዚህ ይጫኑ</a>\n\n"
            f"❌ <a href='{reject_link}'>የለም ለማለት እዚህ ይጫኑ</a>"
        )

        if send_telegram_msg(owner_msg):
            st.success("✅ ትዕዛዝዎ ተልኳል!")
            st.info("ባለቤቱ መኖሩን አረጋግጠው በቴሌግራም መልስ እስኪልኩዎት ይጠብቁ።")
            st.balloons()
        else:
            st.error("ትዕዛዙ አልተላከም::")
    else:
        st.warning("እባክዎ መረጃዎችን በትክክል ይሙሉ!")
