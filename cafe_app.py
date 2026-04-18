import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import qrcode
from io import BytesIO

# --- 1. የቴሌግራም መረጃ ---
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
CHAT_ID = "8779279617"
OWNER_PHONE = "0919299256"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except:
        pass

# --- 2. የገጽ ዝግጅት ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

menu = {
    "በያይነቱ": 50.00, "ሽሮ ፈሰስ": 40.00, "ምስር ወጥ": 45.00,
    "ፓስታ በቲማቲም": 50.00, "ጥብስ": 200.00, "ልዩ ቁርስ": 80.00,
    "ሻይ": 10.00, "ቡና": 20.00, "ለስላሳ": 35.00
}

# --- 3. QR Code (በአዲሱ ሊንክህ የተስተካከለ) ---
app_url = "https://emu-migib.streamlit.app" 
qr_img = qrcode.make(app_url)
buf = BytesIO()
qr_img.save(buf, format="PNG")

# --- 4. Sidebar ---
st.sidebar.title("🍱 እሙ ምግብ ቤት")
st.sidebar.write(f"📞 ባለቤት: {OWNER_PHONE}")
st.sidebar.markdown("---")
st.sidebar.write("📲 ለደንበኞች ያጋሩ")
st.sidebar.image(buf.getvalue(), caption="ይህንን ስካን አድርገው ይዘዙ")

# --- 5. ዋናው ገጽ ---
st.title("🍳 እንኳን ወደ እሙ ምግብ ቤት መጡ")
st.write("ትኩስ ምግቦችን እዚህ ይዘዙ - ወዲያውኑ እናዘጋጃለን!")

customer_name = st.text_input("የእርስዎ ስም")
food = st.selectbox("ምን መመገብ ይፈልጋሉ?", list(menu.keys()))

unit_price = menu[food]
st.info(f"💰 የ፩ {food} ዋጋ፦ **{unit_price:.2f} ብር**")

qty = st.number_input("ብዛት", min_value=1, value=1, step=1)
total_bill = unit_price * qty
st.subheader(f"💵 ጠቅላላ ሂሳብ፦ {total_bill:.2f} ብር")

if st.button("ትዕዛዝ አስተላልፍ 🚀"):
    if customer_name:
        now = datetime.now().strftime("%I:%M %p")
        msg = (f"<b>🔔 አዲስ ትዕዛዝ ደርሷል!</b>\n\n"
               f"👤 <b>ደንበኛ:</b> {customer_name}\n"
               f"🍲 <b>ምግብ:</b> {food}\n"
               f"🔢 <b>ብዛት:</b> {qty}\n"
               f"💵 <b>ጠቅላላ ሂሳብ:</b> {total_bill} ብር\n"
               f"🕒 <b>ሰዓት:</b> {now}")
        
        send_telegram_msg(msg)
        st.success(f"እናመሰግናለን {customer_name}! ትዕዛዝዎ ደርሶናል።")
        st.balloons()
    else:
        st.error("እባክዎ መጀመሪያ ስምዎን ያስገቡ!")
