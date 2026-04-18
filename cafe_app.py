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
        order_id = datetime.now().strftime("%H%M%S")
        now = datetime.now().strftime("%I:%M %p")

        # ለባለቤቱ የሚላኩ መልዕክቶች ተጽፈው እንዲዘጋጁ (Templates)
        yes_msg = urllib.parse.quote(f"ሰላም {customer_name}፣ ደርሶናል እናመሰግናለን! ትዕዛዝዎን እያዘጋጀን ነው።")
        no_msg = urllib.parse.quote(f"ይቅርታ {customer_name}፣ ለጊዜው '{food}' የለም፤ እባክዎ ሌላ ይዘዙ።")
        
        confirm_link = f"https://t.me/{clean_username}?text={yes_msg}"
        reject_link = f"https://t.me/{clean_username}?text={no_msg}"

        # 1. ለባለቤቱ የሚላክ የቴሌግራም መልዕክት
        owner_msg = (
            f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n\n"
            f"👤 <b>ደንበኛ:</b> {customer_name}\n"
            f"🍲 <b>ምግብ:</b> {food} ({qty})\n"
            f"💵 <b>ሂሳብ:</b> {total_bill} ብር\n\n"
            f"👇 <b>መልስ ለመስጠት አንዱን ይጫኑ:</b>\n"
            f"✅ <a href='{confirm_link}'>ደርሶናል ለማለት</a>\n"
            f"❌ <a href='{reject_link}'>የለም ለማለት</a>"
        )

        if send_telegram_msg(owner_msg):
            st.success("✅ ትዕዛዝዎ በተሳካ ሁኔታ ተልኳል!")
            
            # --- 5. ለደንበኛው የሚታይ ሪሲት (Receipt) ---
            st.markdown("---")
            st.markdown(f"""
            <div style="border: 2px dashed #4CAF50; padding: 20px; border-radius: 10px; background-color: #ffffff; color: #333; font-family: sans-serif;">
                <h2 style="text-align: center; color: #4CAF50; margin-bottom: 0;">🧾 እሙ ምግብ ቤት</h2>
                <p style="text-align: center; margin-top: 0; font-size: 14px;">የሽያጭ ማረጋገጫ / Receipt</p>
                <hr>
                <p><b>የትዕዛዝ ቁጥር:</b> #{order_id}</p>
                <p><b>የደንበኛ ስም:</b> {customer_name}</p>
                <p><b>ቀን:</b> {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</p>
                <hr>
                <table style="width:100%">
                    <tr style="border-bottom: 1px solid #ddd;">
                        <th style="text-align:left">ምግብ</th>
                        <th style="text-align:center">ብዛት</th>
                        <th style="text-align:right">ዋጋ</th>
                    </tr>
                    <tr>
                        <td>{food}</td>
                        <td style="text-align:center">{qty}</td>
                        <td style="text-align:right">{unit_price:.2f}</td>
                    </tr>
                </table>
                <hr>
                <h3 style="text-align: right; margin-bottom: 0;">ጠቅላላ ሂሳብ: {total_bill:.2f} ብር</h3>
                <p style="font-size: 12px; color: gray; text-align: center; margin-top: 20px;">
                    ባለቤቱ መኖሩን አረጋግጠው በቴሌግራም @{clean_username} ምላሽ ይሰጡዎታል።
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 ደንበኛ ሆይ፤ ይህንን ሪሲት ስክሪን-ሻት (Screenshot) አድርገው ይያዙ።")
            st.balloons()
        else:
            st.error("ትዕዛዙ አልተላከም:: እባክዎ ኢንተርኔትዎን ያረጋግጡ::")
    else:
        st.warning("እባክዎ ስምዎን እና የቴሌግራም መለያዎን በትክክል ያስገቡ!")
