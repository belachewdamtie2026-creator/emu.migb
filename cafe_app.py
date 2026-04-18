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

# የትዕዛዝ ቅርጫት ዝግጅት (Session State)
if 'cart' not in st.session_state:
    st.session_state.cart = []

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
st.write("እንኳን ደህና መጡ! የሚፈልጉትን ምግቦች መርጠው 'ወደ ቅርጫት ጨምር' የሚለውን ይጫኑ።")

customer_name = st.text_input("የእርስዎ ስም")
telegram_username = st.text_input("የቴሌግራም መለያ (Username)", placeholder="@example")

st.markdown("---")

# --- 5. ምግብ መምረጫ ---
col1, col2 = st.columns([2, 1])
with col1:
    food = st.selectbox("ምን መመገብ ይፈልጋሉ?", list(menu.keys()))
with col2:
    qty = st.number_input("ብዛት", min_value=1, value=1, step=1)

if st.button("ወደ ቅርጫት ጨምር 🛒"):
    st.session_state.cart.append({
        "ምግብ": food,
        "ብዛት": qty,
        "ዋጋ": menu[food] * qty
    })
    st.toast(f"{food} ተጨምሯል!")

# --- 6. የቅርጫት ዝርዝር ማሳያ ---
if st.session_state.cart:
    st.markdown("### 🛒 የመረጧቸው ምግቦች")
    total_bill = 0
    
    # ሰንጠረዥ ለደንበኛው ለማሳየት
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
        c1.write(item["ምግብ"])
        c2.write(f"x{item['ብዛት']}")
        c3.write(f"{item['ዋጋ']:.2f} ብር")
        if c4.button("❌", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()
        total_bill += item["ዋጋ"]

    st.markdown(f"#### 💰 ጠቅላላ ሂሳብ: **{total_bill:.2f} ብር**")

    if st.button("ትዕዛዝ አስተላልፍ 🚀"):
        if customer_name and telegram_username:
            clean_username = telegram_username.replace("@", "").strip()
            order_id = datetime.now().strftime("%H%M%S")
            
            # ለቴሌግራም የሚሆን ዝርዝር ማዘጋጀት
            food_list_msg = ""
            receipt_rows = ""
            for item in st.session_state.cart:
                food_list_msg += f"• {item['ምግብ']} ({item['ብዛት']})\n"
                receipt_rows += f"<tr><td>{item['ምግብ']}</td><td style='text-align:center'>{item['ብዛት']}</td><td style='text-align:right'>{item['ዋጋ']:.2f}</td></tr>"

            yes_msg = urllib.parse.quote(f"ሰላም {customer_name}፣ ትዕዛዝዎ #{order_id} ደርሶናል። እያዘጋጀን ነው።")
            confirm_link = f"https://t.me/{clean_username}?text={yes_msg}"

            owner_msg = (
                f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n\n"
                f"👤 <b>ደንበኛ:</b> {customer_name}\n"
                f"🍲 <b>ምግቦች:</b>\n{food_list_msg}\n"
                f"💵 <b>ጠቅላላ ሂሳብ:</b> {total_bill} ብር\n\n"
                f"✅ <a href='{confirm_link}'>ደርሶናል ለማለት</a>"
            )

            if send_telegram_msg(owner_msg):
                st.success("✅ ትዕዛዝዎ በተሳካ ሁኔታ ተልኳል!")
                
                # --- 7. ለደንበኛው የሚታይ ሪሲት ---
                st.markdown(f"""
                <div style="border: 2px dashed #4CAF50; padding: 20px; border-radius: 10px; background-color: #ffffff; color: #333; font-family: sans-serif;">
                    <h2 style="text-align: center; color: #4CAF50; margin-bottom: 0;">🧾 እሙ ምግብ ቤት</h2>
                    <p style="text-align: center; margin-top: 0; font-size: 14px;">የሽያጭ ማረጋገጫ / Receipt</p>
                    <hr>
                    <p><b>የትዕዛዝ ቁጥር:</b> #{order_id} | <b>ስም:</b> {customer_name}</p>
                    <table style="width:100%">
                        <tr style="border-bottom: 1px solid #ddd;">
                            <th style="text-align:left">ምግብ</th>
                            <th style="text-align:center">ብዛት</th>
                            <th style="text-align:right">ዋጋ</th>
                        </tr>
                        {receipt_rows}
                    </table>
                    <hr>
                    <h3 style="text-align: right;">ጠቅላላ ሂሳብ: {total_bill:.2f} ብር</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.cart = [] # ትዕዛዙ ካለቀ ቅርጫቱን ባዶ ማድረግ
                st.balloons()
            else:
                st.error("ትዕዛዙ አልተላከም:: እባክዎ ኢንተርኔትዎን ያረጋግጡ::")
        else:
            st.warning("እባክዎ ስምዎን እና የቴሌግራም መለያዎን በትክክል ያስገቡ!")
else:
    st.info("💡 ገና ምንም ምግብ አልመረጡም። ከላይ መርጠው 'ወደ ቅርጫት ጨምር' የሚለውን ይጫኑ።")
