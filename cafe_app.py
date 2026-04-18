import streamlit as st
from datetime import datetime
import requests
import qrcode
from io import BytesIO
import urllib.parse

# --- 1. የቴሌግራም መረጃ (ደህንነት፡ ከተቻለ በ st.secrets ይጠቀሙ) ---
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
customer_name = st.text_input("የእርስዎ ስም", placeholder="ስምዎን እዚህ ያስገቡ")
telegram_username = st.text_input("የቴሌግራም መለያ (Username)", placeholder="@example")

st.markdown("---")

# --- 5. የተሻሻለ ምግብ መምረጫ (ለየብቻ ወይም በአንድ እቃ) ---
st.subheader("🍽 ምግብ ይምረጡ")
selection_mode = st.radio("የአቀራረብ ምርጫ", ["ለየብቻ (ነጠላ)", "በአንድ እቃ (Combo/Platter)"])

if selection_mode == "ለየብቻ (ነጠላ)":
    col1, col2 = st.columns([3, 1])
    with col1:
        food = st.selectbox("የሚፈልጉትን ምግብ ይምረጡ", list(menu.keys()))
    with col2:
        qty = st.number_input("ብዛት", min_value=1, value=1)
    
    if st.button("ወደ ቅርጫት ጨምር 🛒"):
        st.session_state.cart.append({
            "ምግብ": food, 
            "ብዛት": qty, 
            "ዋጋ": menu[food] * qty,
            "አቀራረብ": "ለየብቻ"
        })
        st.toast(f"{food} ተጨምሯል!")

else:
    selected_foods = st.multiselect("በአንድ እቃ እንዲቀላቀሉ የሚፈልጓቸውን ምግቦች ይምረጡ", list(menu.keys()))
    if selected_foods:
        total_combo_price = sum(menu[f] for f in selected_foods)
        st.info(f"የዚህ ጥምረት ጠቅላላ ዋጋ፦ **{total_combo_price:.2f} ብር**")
        
        if st.button("ጥምረቱን ወደ ቅርጫት ጨምር 🍱"):
            combo_name = " + ".join(selected_foods)
            st.session_state.cart.append({
                "ምግብ": f"ጥምረት: {combo_name}", 
                "ብዛት": 1, 
                "ዋጋ": total_combo_price,
                "አቀራረብ": "በአንድ እቃ"
            })
            st.success("ጥምረቱ ተጨምሯል!")
            st.rerun()

st.markdown("---")

# --- 6. የቅርጫት ዝርዝር እና ትዕዛዝ ማስተላለፊያ ---
if st.session_state.cart:
    st.markdown("### 🛒 የመረጧቸው ምግቦች")
    total_bill = 0
    receipt_rows = ""
    food_summary = ""
    
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3 = st.columns([4, 2, 1])
        c1.write(f"**{item['ምግብ']}**\n({item['አቀራረብ']})")
        c2.write(f"{item['ዋጋ']:.2f} ብር")
        if c3.button("❌", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()
            
        total_bill += item["ዋጋ"]
        receipt_rows += f"<tr><td>{item['ምግብ']}</td><td style='text-align:right'>{item['ዋጋ']:.2f}</td></tr>"
        icon = "🍱" if item['አቀራረብ'] == "በአንድ እቃ" else "🍛"
        food_summary += f"{icon} {item['ምግብ']} (x{item['ብዛት']}) - [{item['አቀራረብ']}]\n"

    st.markdown(f"#### 💰 ጠቅላላ ሂሳብ: **{total_bill:.2f} ብር**")

    if st.button("ትዕዛዝ አስተላልፍ 🚀"):
        if customer_name and telegram_username:
            clean_username = telegram_username.replace("@", "").strip()
            order_id = datetime.now().strftime("%H%M%S")
            
            # ለደንበኛው የሚላክ መልስ ሊንክ
            yes_msg = urllib.parse.quote(f"ሰላም {customer_name}፣ ትዕዛዝዎ #{order_id} ደርሶናል። እያዘጋጀን ነው።")
            no_msg = urllib.parse.quote(f"ይቅርታ {customer_name}፣ ያዘዙት ምግብ ለአሁኑ አልቋል።")
            confirm_link = f"https://t.me/{clean_username}?text={yes_msg}"
            reject_link = f"https://t.me/{clean_username}?text={no_msg}"

            owner_msg = (
                f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n\n"
                f"👤 <b>ደንበኛ:</b> {customer_name}\n"
                f"📝 <b>ዝርዝር:</b>\n{food_summary}\n"
                f"💵 <b>ጠቅላላ ሂሳብ:</b> {total_bill} ብር\n\n"
                f"👇 <b>ለደንበኛው መልስ ለመስጠት:</b>\n"
                f"✅ <a href='{confirm_link}'>አለ (Confirm)</a>\n"
                f"❌ <a href='{reject_link}'>የለም (Reject)</a>"
            )

            if send_telegram_msg(owner_msg):
                st.success("✅ ትዕዛዝዎ በተሳካ ሁኔታ ተልኳል!")
                # የደረሰኝ ማሳያ
                st.markdown(f"""
                <div style="border: 2px dashed #4CAF50; padding: 20px; border-radius: 10px; background-color: #f9f9f9; color: #333;">
                    <h2 style="text-align: center; color: #4CAF50;">🧾 እሙ ምግብ ቤት</h2>
                    <p><b>ትዕዛዝ ቁጥር:</b> #{order_id} | <b>ስም:</b> {customer_name}</p>
                    <table style="width:100%">{receipt_rows}</table>
                    <hr><h3 style="text-align: right;">ጠቅላላ: {total_bill:.2f} ብር</h3>
                </div>""", unsafe_allow_html=True)
                st.session_state.cart = [] 
                st.balloons()
            else:
                st.error("ትዕዛዙን መላክ አልተቻለም። እባክዎ ኢንተርኔትዎን ያረጋግጡ።")
        else:
            st.warning("እባክዎ ስምዎን እና የቴሌግራም መለያዎን ያስገቡ!")
else:
    st.info("ቅርጫትዎ ባዶ ነው። እባክዎ ምግብ ይምረጡ።")
