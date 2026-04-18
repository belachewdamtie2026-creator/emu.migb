import streamlit as st
from datetime import datetime
import requests
import qrcode
from io import BytesIO
import urllib.parse

# --- 1. የቴሌግራም መረጃ ---
BOT_TOKEN = st.secrets.get("BOT_TOKEN", "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI")
CHAT_ID = st.secrets.get("CHAT_ID", "1066005872")

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        return requests.post(url, data=payload).status_code == 200
    except:
        return False

# --- 2. የገጽ ዝግጅት ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

menu = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

st.title("🍳 እሙ ምግብ ቤት")
st.write("የሚፈልጉትን ምግቦች ይምረጡና ብዛታቸውን ያስገቡ።")

# --- 3. የተጠቃሚ መረጃ ---
col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input("👤 የእርስዎ ስም")
with col2:
    telegram_username = st.text_input("✈️ የቴሌግራም መለያ", placeholder="@username")

# --- 4. የብዙ ምግብ ምርጫ ---
selected_foods = st.multiselect("🍲 ምግቦችን ይምረጡ", list(menu.keys()))

order_items = []
grand_total = 0

if selected_foods:
    st.write("---")
    st.write("#### የትዕዛዝ ዝርዝር")
    for food in selected_foods:
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            st.write(f"**{food}** ({menu[food]} ብር)")
        with c2:
            qty = st.number_input(f"ብዛት ({food})", min_value=1, value=1, key=f"qty_{food}")
        with c3:
            item_total = menu[food] * qty
            st.write(f"**{item_total:.2f} ብር**")
            order_items.append({"name": food, "qty": qty, "subtotal": item_total})
            grand_total += item_total

    st.markdown(f"## 💰 አጠቃላይ ድምር: `{grand_total:.2f} ብር`")

# --- 5. ትዕዛዝ ማስተላለፊያ ---
if st.button("ትዕዛዝ አስተላልፍ 🚀"):
    if not customer_name or not telegram_username:
        st.warning("⚠️ እባክዎ ስም እና የቴሌግራም መለያ ያስገቡ!")
    elif not selected_foods:
        st.warning("⚠️ ቢያንስ አንድ ምግብ መምረጥ አለብዎት!")
    else:
        clean_username = telegram_username.replace("@", "").strip()
        order_id = datetime.now().strftime("%H%M%S")
        
        # የትዕዛዝ ዝርዝር ለቴሌግራም
        food_details_msg = ""
        receipt_rows = ""
        for item in order_items:
            food_details_msg += f"• {item['name']} ({item['qty']})\n"
            receipt_rows += f"<tr><td>{item['name']}</td><td style='text-align:center'>{item['qty']}</td><td style='text-align:right'>{item['subtotal']:.2f}</td></tr>"

        # ለባለቤቱ የሚላክ መልዕክት
        owner_msg = (
            f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n\n"
            f"👤 <b>ደንበኛ:</b> {customer_name}\n"
            f"🍲 <b>ዝርዝር:</b>\n{food_details_msg}"
            f"💵 <b>ጠቅላላ ሂሳብ:</b> {grand_total} ብር\n\n"
            f"✅ <a href='https://t.me/{clean_username}'>ለደንበኛው መልስ ስጥ</a>"
        )

        if send_telegram_msg(owner_msg):
            st.success("✅ ትዕዛዝዎ ተልኳል!")
            
            # ዲጂታል ሪሲት
            st.markdown(f"""
            <div style="border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background-color: white; color: black;">
                <h2 style="text-align: center; color: #4CAF50;">🧾 እሙ ምግብ ቤት</h2>
                <p><b>ትዕዛዝ ቁጥር:</b> #{order_id} | <b>ደንበኛ:</b> {customer_name}</p>
                <hr>
                <table style="width:100%">
                    <tr><th>ምግብ</th><th style='text-align:center'>ብዛት</th><th style='text-align:right'>ዋጋ</th></tr>
                    {receipt_rows}
                </table>
                <hr>
                <h3 style="text-align: right;">ጠቅላላ: {grand_total:.2f} ብር</h3>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
        else:
            st.error("❌ ችግር ተፈጥሯል። እባክዎ ድጋሚ ይሞክሩ።")
