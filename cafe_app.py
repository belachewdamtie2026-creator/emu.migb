import streamlit as st
from datetime import datetime
import requests
import qrcode
from io import BytesIO

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
st.write("እንኳን ደህና መጡ! የሚፈልጉትን ምግብ ይምረጡ።")

customer_name = st.text_input("የእርስዎ ስም")
telegram_username = st.text_input("የቴሌግራም መለያ (Username)", placeholder="@example")
food = st.selectbox("ምን መመገብ ይፈልጋሉ?", list(menu.keys()))

unit_price = menu[food]
qty = st.number_input("ብዛት", min_value=1, value=1, step=1)
total_bill = unit_price * qty

st.markdown(f"### 💰 ጠቅላላ ሂሳብ: **{total_bill:.2f} ብር**")

if st.button("ትዕዛዝ አስተላልፍ 🚀"):
    if customer_name and telegram_username:
        clean_username = telegram_username.replace("@", "").strip()
        customer_link = f"https://t.me/{clean_username}"
        now = datetime.now().strftime("%I:%M %p")
        order_id = datetime.now().strftime("%H%M%S")

        # ለባለቤቱ የሚላክ መልዕክት
        owner_msg = (
            f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n\n"
            f"👤 <b>ደንበኛ:</b> <a href='{customer_link}'>{customer_name}</a>\n"
            f"🍲 <b>ምግብ:</b> {food}\n"
            f"🔢 <b>ብዛት:</b> {qty}\n"
            f"💵 <b>ሂሳብ:</b> {total_bill} ብር\n"
            f"🕒 <b>ሰዓት:</b> {now}\n\n"
            f"👇 <b>ለደንበኛው መልስ ለመስጠት ስሙን ይጫኑ!</b>"
        )

        if send_telegram_msg(owner_msg):
            # --- 5. ለደንበኛው የሚታይ ማረጋገጫ ---
            st.success("✅ ትዕዛዝዎ በተሳካ ሁኔታ ተልኳል!")
            
            # የደረሰኝ ዲዛይን
            st.markdown(f"""
            <div style="border: 2px solid #4CAF50; padding: 15px; border-radius: 10px; background-color: #f9f9f9; color: #333;">
                <h3 style="text-align: center; color: #4CAF50;">🧾 የትዕዛዝ ማረጋገጫ</h3>
                <p><b>የደንበኛ ስም:</b> {customer_name}</p>
                <p><b>የታዘዘው ምግብ:</b> {food} ({qty})</p>
                <p><b>ጠቅላላ ሂሳብ:</b> {total_bill:.2f} ብር</p>
                <hr>
                <p style="text-align: center; font-weight: bold;">ባለቤቱ አሁን በቴሌግራም የሚከተለውን መልስ ይልኩልዎታል፡</p>
                <div style="background-color: #e1f5fe; padding: 10px; border-radius: 5px; margin-bottom: 5px;">
                    ✅ <b>"ደርሶናል እናመሰግናለን! ትዕዛዝዎን እያዘጋጀን ነው።"</b>
                </div>
                <div style="background-color: #ffebee; padding: 10px; border-radius: 5px;">
                    ❌ <b>"ይቅርታ ለጊዜው ይሄ ምግብ የለም እባክዎ ሌላ ይዘዙ።"</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info(f"💡 {customer_name} ሆይ፤ እባክዎ ቴሌግራምዎ ላይ ባለቤቱ መልስ እስኪልኩዎት ይጠብቁ።")
            st.balloons()
        else:
            st.error("ትዕዛዙን መላክ አልተቻለም። እባክዎ ኢንተርኔትዎን ያረጋግጡ።")
    else:
        st.warning("እባክዎ ስምዎን እና የቴሌግራም መለያዎን ያስገቡ!")
