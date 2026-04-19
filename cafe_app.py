import streamlit as st
from datetime import datetime
import requests
import qrcode
from io import BytesIO
import urllib.parse

# --- 1. የቴሌግራም መረጃ ---
# ማሳሰቢያ፡ ለደህንነት ሲባል እነዚህን በ Streamlit Secrets ውስጥ ቢያስቀምጡ ይመከራል
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
CHAT_ID = "1066005872"
OWNER_PHONE = "0919299256"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "HTML", 
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except:
        return False

# --- 2. የገጽ ዝግጅት ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

if 'cart' not in st.session_state:
    st.session_state.cart = []

# የምግብ ዝርዝር እና ዋጋ
menu = {
    "በያይነት": 100.00, "ሽሮ ፈሰስ": 70.00, "ምስር ወጥ": 80.00,
    "ፓስታ በአትክልት": 90.00, "ጥብስ": 200.00, "ስጋ ፍርፍር": 160.00,
    "ዳቦ": 10.00, "እንቁላል": 120.00, "ድንች ፍርፍር": 80.00
}

# --- 3. Sidebar (QR Code) ---
app_url = "https://emumigb-2018.streamlit.app/" 
qr_img = qrcode.make(app_url)
buf = BytesIO()
qr_img.save(buf, format="PNG")

st.sidebar.title("🍱 እሙ ምግብ ቤት")
st.sidebar.write(f"📞 ባለቤት: {OWNER_PHONE}")
st.sidebar.image(buf.getvalue(), caption="ይህንን ስካን አድርገው ይዘዙ")

# --- 4. ዋናው ገጽ ---
st.title("🍳 እሙ ምግብ ቤት")
customer_name = st.text_input("የእርስዎ ስም", placeholder="ሙሉ ስምዎን ያስገቡ")
telegram_username = st.text_input("የቴሌግራም መለያ (Username)", placeholder="@example")

st.markdown("---")

# --- 5. የምግብ መምረጫ ክፍል ---
st.subheader("🍽 ምን መመገብ ይፈልጋሉ?")
selection_mode = st.radio("የአቀራረብ ምርጫ", ["ለየብቻ (ነጠላ)", "በአንድ እቃ (Combo)"], horizontal=True)

if selection_mode == "ለየብቻ (ነጠላ)":
    col1, col2 = st.columns([3, 1])
    with col1:
        food = st.selectbox("ምግብ ይምረጡ", list(menu.keys()))
    with col2:
        qty = st.number_input("ብዛት", min_value=1, value=1, step=1)
    
    if st.button("ወደ ቅርጫት ጨምር 🛒", use_container_width=True):
        st.session_state.cart.append({
            "ምግብ": food, 
            "ብዛት": qty, 
            "ዋጋ": menu[food] * qty,
            "አቀራረብ": "ለየብቻ"
        })
        st.toast(f"{food} ተጨምሯል!")

else:
    # በአንድ እቃ (Combo) ለሚፈልጉ
    selected_foods = st.multiselect("በአንድ እቃ እንዲቀላቀሉ የሚፈልጓቸውን ምግቦች ይምረጡ", list(menu.keys()))
    
    if selected_foods:
        st.info("ለእያንዳንዱ ምግብ የሚፈልጉትን መጠን (Quantity) ያስገቡ፡")
        combo_details = []
        total_combo_price = 0
        
        for f in selected_foods:
            c_name, c_qty = st.columns([3, 2])
            with c_name:
                st.write(f"**{f}**")
            with c_qty:
                q = st.number_input(f"መጠን", min_value=1, value=1, step=1, key=f"combo_{f}")
            
            item_price = menu[f] * q
            total_combo_price += item_price
            combo_details.append(f"{f} (x{q})")

        st.markdown(f"**የጥምረቱ ድምር ሂሳብ፦ {total_combo_price:.2f} ብር**")
        
        if st.button("ይህን ጥምረት ወደ ቅርጫት ጨምር 🍱", use_container_width=True):
            combo_summary = " + ".join(combo_details)
            st.session_state.cart.append({
                "ምግብ": f"ጥምረት: {combo_summary}", 
                "ብዛት": 1, 
                "ዋጋ": total_combo_price,
                "አቀራረብ": "በአንድ እቃ"
            })
            st.success("ጥምረቱ ወደ ቅርጫት ተጨምሯል!")
            st.rerun()

st.markdown("---")

# --- 6. የቅርጫት ዝርዝር እና ትዕዛዝ ማስተላለፊያ ---
if st.session_state.cart:
    st.markdown("### 🛒 የመረጧቸው ምግቦች")
    total_bill = 0
    receipt_rows = ""
    food_summary_for_tg = ""
    
    for i, item in enumerate(st.session_state.cart):
        with st.container():
            c1, c2, c3 = st.columns([4, 2, 1])
            c1.write(f"**{item['ምግብ']}**\n({item['አቀራረብ']})")
            c2.write(f"{item['ዋጋ']:.2f} ብር")
            if c3.button("❌", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
            
            total_bill += item["ዋጋ"]
            receipt_rows += f"<tr><td style='padding:5px;'>{item['ምግብ']}</td><td style='text-align:right;'>{item['ዋጋ']:.2f}</td></tr>"
            icon = "🍱" if item['አቀራረብ'] == "በአንድ እቃ" else "🍛"
            food_summary_for_tg += f"{icon} {item['ምግብ']} - {item['ዋጋ']:.2f} ብር\n"

    st.markdown(f"### 💰 ጠቅላላ ሂሳብ: **{total_bill:.2f} ብር**")

    if st.button("ትዕዛዝ አስተላልፍ 🚀", use_container_width=True):
        if customer_name and telegram_username:
            clean_username = telegram_username.replace("@", "").strip()
            order_id = datetime.now().strftime("%H%M%S")
            
            # መልስ ለመስጠት የሚያስችሉ ሊንኮች
            yes_url = f"https://t.me/{clean_username}?text=" + urllib.parse.quote(f"ሰላም {customer_name}፣ ትዕዛዝዎ #{order_id} ደርሶናል። እያዘጋጀን ነው።")
            no_url = f"https://t.me/{clean_username}?text=" + urllib.parse.quote(f"ይቅርታ {customer_name}፣ ያዘዙት ምግብ ለአሁኑ ስለተጠናቀቀ ማቅረብ አልቻልንም።")

            owner_msg = (
                f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n\n"
                f"👤 <b>ደንበኛ:</b> {customer_name}\n"
                f"📝 <b>ዝርዝር:</b>\n{food_summary_for_tg}\n"
                f"💵 <b>ጠቅላላ ሂሳብ:</b> {total_bill:.2f} ብር\n\n"
                f"👇 <b>ለደንበኛው መልስ ይስጡ:</b>\n"
                f"✅ <a href='{yes_url}'>አለ/ተቀብለናል</a>\n"
                f"❌ <a href='{no_url}'>የለም/አልቋል</a>"
            )

            if send_telegram_msg(owner_msg):
                st.success("✅ ትዕዛዝዎ ለባለቤቱ ተልኳል!")
                # የደረሰኝ ዲዛይን
                st.markdown(f"""
                <div style="border: 2px solid #4CAF50; padding: 15px; border-radius: 10px; background-color: #ffffff; font-family: sans-serif;">
                    <h2 style="text-align: center; color: #4CAF50; margin-top:0;">🧾 እሙ ምግብ ቤት</h2>
                    <p style="margin:5px 0;"><b>ትዕዛዝ #:</b> {order_id}</p>
                    <p style="margin:5px 0;"><b>ደንበኛ:</b> {customer_name}</p>
                    <hr>
                    <table style="width:100%; border-collapse: collapse;">
                        {receipt_rows}
                    </table>
                    <hr>
                    <h3 style="text-align: right; margin:10px 0;">ጠቅላላ: {total_bill:.2f} ብር</h3>
                    <p style="text-align: center; font-size: 12px; color: #888;">ስለመረጡን እናመሰግናለን!</p>
                </div>""", unsafe_allow_html=True)
                
                st.session_state.cart = [] # ቅርጫቱን ባዶ ማድረግ
                st.balloons()
            else:
                st.error("ትዕዛዙን መላክ አልተቻለም። እባክዎ በስልክ ይደውሉ ወይም ኢንተርኔትዎን ያረጋግጡ።")
        else:
            st.error("እባክዎ ስምዎን እና የቴሌግራም መለያዎን (Username) ያስገቡ!")
else:
    st.info("ቅርጫትዎ ባዶ ነው። እባክዎ የሚፈልጉትን ምግብ መርጠው ይጨምሩ።")
