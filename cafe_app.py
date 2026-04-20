import streamlit as st
import pandas as pd
import requests
import qrcode
from io import BytesIO
import threading
import telebot

# --- 1. ኮንፊገሬሽን (Telegram) ---
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
OWNER_CHAT_ID = "1066005872"  # የባለቤቱ Chat ID

bot = telebot.TeleBot(BOT_TOKEN)

# --- 2. የቴሌግራም ቦት ምላሽ ሰጪ (Backend Handler) ---
# ይህ ክፍል ባለቤቱ ቁልፉን ሲጫን ለደንበኛው መልዕክት ይልካል
@bot.callback_query_handler(func=lambda call: True)
def handle_owner_response(call):
    try:
        # ዳታውን መከፋፈል (status|customer_id|customer_name)
        data = call.data.split("|")
        status = data[0]
        customer_id = data[1]
        customer_name = data[2]

        if status == "accept":
            response_text = f"ሰላም {customer_name}፣ ትዕዛዝዎ ተቀባይነት አግኝቷል! ✅ በቅርቡ ይደርሳል።"
            bot.send_message(customer_id, response_text)
            bot.edit_message_text(f"{call.message.text}\n\n<b>ሁኔታ፦ ተቀባይነት አግኝቷል ✅</b>", 
                                 OWNER_CHAT_ID, call.message.message_id, parse_mode="HTML")
        
        elif status == "reject":
            response_text = f"ይቅርታ {customer_name}፣ ያዘዙት ምግብ ስለሌለ ትዕዛዝዎ ተሰርዟል። ❌"
            bot.send_message(customer_id, response_text)
            bot.edit_message_text(f"{call.message.text}\n\n<b>ሁኔታ፦ አልቋል ተብሏል ❌</b>", 
                                 OWNER_CHAT_ID, call.message.message_id, parse_mode="HTML")
    except Exception as e:
        print(f"Error: {e}")

# ቦቱን በስተጀርባ (Background) ለማንቀሳቀስ
def run_bot():
    bot.polling(none_stop=True)

if "bot_thread" not in st.session_state:
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    st.session_state.bot_thread = True

# --- 3. የዌብሳይቱ (Streamlit) ገጽ ዝግጅት ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #fdfdfd; }
    .main-header { text-align: center; color: #E64A19; font-weight: bold; }
    .order-box {
        background-color: white; padding: 15px; border-radius: 12px;
        margin-bottom: 10px; border-left: 6px solid #E64A19;
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
st.sidebar.markdown("<h2 style='text-align: center;'>🍱 እሙ ምግብ ቤት</h2>", unsafe_allow_html=True)
app_url = "https://emumigb-2018.streamlit.app/" 
qr_img = qrcode.make(app_url)
buf = BytesIO()
qr_img.save(buf, format="PNG")
st.sidebar.image(buf.getvalue(), caption="በስልክዎ ስካን አድርገው ይዘዙ")
st.sidebar.warning("ምላሹ በቴሌግራም እንዲደርሶት @userinfobot ላይ የቴሌግራም ID ቁጥርዎን ይወቁ።")

# --- ዋናው ክፍል ---
st.markdown("<h1 class='main-header'>🍳 እሙ ምግብ ቤት</h1>", unsafe_allow_html=True)

if 'cart' not in st.session_state:
    st.session_state.cart = []

col_a, col_b = st.columns(2)
first_name = col_a.text_input("👤 ስም", placeholder="የመጀመሪያ ስም")
customer_chat_id = col_b.text_input("🆔 የቴሌግራም Chat ID", placeholder="ለምሳሌ፦ 12345678")

st.divider()

packing_style = st.radio("**የአቀራረብ ሁኔታ ይምረጡ**", ["ለየብቻ", "በአንድ እቃ"], horizontal=True)

food_items_to_add = []
if packing_style == "በአንድ እቃ":
    selected_foods = st.multiselect("በአንድ እቃ የሚቀላቀሉ ምግቦችን ይምረጡ", list(MENU.keys()))
    if selected_foods:
        for f in selected_foods:
            c1, c2 = st.columns([3, 1])
            with c1: st.write(f"**{f}**")
            qty = c2.number_input("ብዛት", 1, 10, 1, key=f"mixed_{f}", label_visibility="collapsed")
            food_items_to_add.append({"ምግብ": f, "ብዛት": qty})
else:
    f = st.selectbox("የሚፈልጉትን ምግብ ይምረጡ", list(MENU.keys()))
    qty = st.number_input("ብዛት", 1, 20, 1)
    food_items_to_add.append({"ምግብ": f, "ብዛት": qty})

if st.button("ወደ ቅርጫት ጨምር 🛒", use_container_width=True):
    if food_items_to_add:
        if packing_style == "በአንድ እቃ":
            details = ", ".join([f"{i['ምግብ']} (x{i['ብዛት']})" for i in food_items_to_add])
            price = sum([MENU[i['ምግብ']] * i['ብዛት'] for i in food_items_to_add])
            st.session_state.cart.append({"ዝርዝር": details, "ሁኔታ": "በአንድ እቃ", "ዋጋ": price})
        else:
            for i in food_items_to_add:
                st.session_state.cart.append({"ዝርዝር": f"{i['ምግብ']} (x{i['ብዛት']})", "ሁኔታ": "ለየብቻ", "ዋጋ": MENU[i['ምግብ']] * i['ብዛት']})
        st.toast("✅ ተጨምሯል")

# የቅርጫት እይታ እና ትዕዛዝ ማስተላለፊያ
if st.session_state.cart:
    st.divider()
    total_bill = sum(item['ዋጋ'] for item in st.session_state.cart)
    summary = "\n".join([f"• {item['ዝርዝር']} [{item['ሁኔታ']}]" for item in st.session_state.cart])
    
    st.markdown(f"### ጠቅላላ: {total_bill:.2f} ብር")
    
    if st.button("ትዕዛዝ አስተላልፍ 🚀", use_container_width=True):
        if first_name and customer_chat_id:
            # ለባለቤቱ መልዕክት መላክ
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton("አለ ✅", callback_data=f"accept|{customer_chat_id}|{first_name}"),
                telebot.types.InlineKeyboardButton("የለም ❌", callback_data=f"reject|{customer_chat_id}|{first_name}")
            )
            
            owner_msg = f"🔔 <b>አዲስ ትዕዛዝ</b>\n👤 ደንበኛ: {first_name}\n🆔 ID: {customer_chat_id}\n📝 ዝርዝር:\n{summary}\n💰 ጠቅላላ: {total_bill} ብር"
            bot.send_message(OWNER_CHAT_ID, owner_msg, parse_mode="HTML", reply_markup=keyboard)
            
            st.success(f"እናመሰግናለን {first_name}! ትዕዛዝዎ ተልኳል። ባለቤቱ 'አለ' ወይም 'የለም' ሲል በቴሌግራምዎ መልዕክት ይደርሶታል።")
            st.session_state.cart = []
            st.balloons()
        else:
            st.error("እባክዎ ትዕዛዙን ለመላክ ስምዎን እና የቴሌግራም ID ቁጥርዎን ያስገቡ።")

st.markdown(f"<p style='text-align:center; color:#718096; font-size:11px; margin-top:50px;'>Developer: <b>Belachew Damtie</b></p>", unsafe_allow_html=True)
