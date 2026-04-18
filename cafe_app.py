import streamlit as st
from datetime import datetime
import requests

# --- 1. የቴሌግራም መረጃ ---
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
CHAT_ID = "1066005872"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except:
        return False

# --- 2. የገጽ ዝግጅት ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

# --- 3. ቅርጫት (Cart) ማስተዳደሪያ ---
# ይህ ክፍል ደንበኛው የመረጣቸውን ምግቦች በጊዜያዊነት ይይዛል
if 'cart' not in st.session_state:
    st.session_state.cart = []

menu = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

st.title("🍳 እሙ ምግብ ቤት")
st.write("የሚፈልጉትን ምግብ ይምረጡና 'ወደ ቅርጫት ጨምር' የሚለውን ይጫኑ።")

# --- 4. ምግብ መምረጫ ---
col1, col2 = st.columns([3, 1])

with col1:
    selected_food = st.selectbox("ምግብ ይምረጡ", list(menu.keys()))
with col2:
    quantity = st.number_input("ብዛት", min_value=1, value=1)

if st.button("ወደ ቅርጫት ጨምር 🛒"):
    # አዲስ ምርጫ ወደ ዝርዝሩ መጨመር
    item_price = menu[selected_food] * quantity
    st.session_state.cart.append({
        "food": selected_food,
        "qty": quantity,
        "price": item_price
    })
    st.toast(f"{selected_food} ተጨምሯል!")

# --- 5. የተመረጡ ምግቦች ዝርዝር (ይህ ነው ከአንድ በላይ የሚያሳየው) ---
if st.session_state.cart:
    st.subheader("📋 የእርስዎ የትዕዛዝ ዝርዝር")
    total_bill = 0
    
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
        c1.write(f"🍴 {item['food']}")
        c2.write(f"x{item['qty']}")
        c3.write(f"{item['price']:.2f} ብር")
        if c4.button("❌", key=f"remove_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()
        total_bill += item['price']
    
    st.write("---")
    st.markdown(f"### 💰 ጠቅላላ ድምር: **{total_bill:.2f} ብር**")

    # --- 6. ማዘዣ (Checkout) ---
    st.subheader("👤 የእርስዎን መረጃ ያስገቡ")
    name = st.text_input("ስም")
    tg_user = st.text_input("የቴሌግራም መለያ (ለምሳሌ፦ @username)")

    if st.button("ትዕዛዙን አሁን አስተላልፍ 🚀"):
        if name and tg_user:
            order_id = datetime.now().strftime("%H%M%S")
            
            # የትዕዛዝ ዝርዝሩን ለቴሌግራም ማዘጋጀት
            order_details = ""
            for item in st.session_state.cart:
                order_details += f"• {item['food']} ({item['qty']}) - {item['price']} ብር\n"
            
            owner_message = (
                f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n\n"
                f"👤 <b>ደንበኛ:</b> {name}\n"
                f"✈️ <b>ቴሌግራም:</b> {tg_user}\n"
                f"🍱 <b>ዝርዝር:</b>\n{order_details}\n"
                f"💵 <b>ጠቅላላ ሂሳብ:</b> {total_bill} ብር"
            )

            if send_telegram_msg(owner_message):
                st.success("✅ ትዕዛዝዎ ተልኳል! እናመሰግናለን።")
                st.session_state.cart = [] # ትዕዛዙ ካለቀ ቅርጫቱን ባዶ ማድረግ
                st.balloons()
            else:
                st.error("መልዕክቱ አልተላከም። ኢንተርኔትዎን ያረጋግጡ።")
        else:
            st.warning("እባክዎ ስም እና ቴሌግራም ያስገቡ።")
else:
    st.info("ገና ምንም ምግብ አልመረጡም።")
