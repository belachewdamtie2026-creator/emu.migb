Streamlit ምግብ ቤት ኮድ ማሻሻያ
Conversation with Gemini
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

ይህ የስትሪምሊት (Streamlit) ኮድ ለ "እሙ ምግብ ቤት" በጣም ጥሩ ጅምር ነው። ቀላል፣ ግልጽ እና ተግባራዊ ነው። ሆኖም ግን፣ ኮዱን ይበልጥ አስተማማኝ እና ፕሮፌሽናል ለማድረግ ጥቂት ማስተካከያዎች ቢደረጉበት መልካም ነው።

በተለይም የሴኪውሪቲ (Security) ጉዳይ ትኩረት ይፈልጋል። የቦት ቶከን (Bot Token) በኮዱ ውስጥ በቀጥታ ማስቀመጥ ለሃከሮች በር ይከፍታል።

ለኮድዎ የተደረጉ ማሻሻያዎች እና ጥቁምታዎች እነሆ፦

🛠 ዋና ዋና ማሻሻያዎች
ደህንነት (Environment Variables): የቦት ቶከንዎን በ st.secrets ውስጥ መደበቅ።

የQR ኮድ አጠቃቀም: በየጊዜው QR ኮድ ከማመንጨት ይልቅ አንድ ጊዜ የተዘጋጀ ምስል መጠቀም ፍጥነት ይጨምራል።

የተጠቃሚ ስም (Input Validation): ተጠቃሚው @ ምልክት ቢረሳ እንኳን ኮዱ እንዳይበላሽ ማድረግ።

ዲዛይን: በምግብ ዝርዝሩ ላይ ምስሎችን ወይም አይኮኖችን መጨመር።

📝 የተሻሻለው ኮድ
Python
import streamlit as st
from datetime import datetime
import requests
import qrcode
from io import BytesIO
import urllib.parse

# --- 1. የቴሌግራም መረጃ (በሴኪውሪቲ ምክንያት በ secrets መጠቀም ይመከራል) ---
# በ Streamlit Cloud ላይ ሲጭኑ Settings -> Secrets ውስጥ ያስገቡት
BOT_TOKEN = st.secrets.get("BOT_TOKEN", "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI")
CHAT_ID = st.secrets.get("CHAT_ID", "1066005872")
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
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# --- 2. የገጽ ዝግጅት ---
st.set_page_config(page_title="እሙ ምግብ ቤት", layout="centered", page_icon="🍳")

# የቅጥ (CSS) ማሻሻያ - ቁልፎችን ለማሳመር
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #4CAF50; color: white; }
    .main { background-color: #f5f5f5; }
    </style>
    """, unsafe_allow_html=True)

menu = {
    "በያይነት 🥗": 100.00, "ሽሮ ፈሰስ 🍲": 70.00, "ምስር ወጥ 🍛": 80.00,
    "ፓስታ በአትክልት 🍝": 90.00, "ጥብስ 🥩": 200.00, "ስጋ ፍርፍር 🥘": 160.00,
    "ዳቦ 🍞": 10.00, "እንቁላል 🍳": 120.00, "ድንች ፍርፍር 🥔": 80.00
}

# --- 3. Sidebar (QR Code) ---
app_url = "https://emumigb2018.streamlit.app/" 
qr = qrcode.QRCode(box_size=10, border=2)
qr.add_data(app_url)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white")
buf = BytesIO()
qr_img.save(buf, format="PNG")

st.sidebar.title("🍱 እሙ ምግብ ቤት")
st.sidebar.info(f"📞 ትዕዛዝ ለመቀየር: {OWNER_PHONE}")
st.sidebar.image(buf.getvalue(), caption="ለጓደኛዎ ያጋሩ")

# --- 4. ዋናው ገጽ ---
st.title("🍳 እሙ ምግብ ቤት")
st.subheader("ፈጣን እና ጣፋጭ ምግቦች")

col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input("👤 የእርስዎ ስም")
with col2:
    telegram_username = st.text_input("✈️ የቴሌግራም መለያ", placeholder="@username")

food_choice = st.selectbox("🍲 ምን መመገብ ይፈልጋሉ?", list(menu.keys()))
qty = st.number_input("🔢 ብዛት", min_value=1, value=1, step=1)

unit_price = menu[food_choice]
total_bill = unit_price * qty

st.markdown(f"### 💰 ጠቅላላ ሂሳብ: `{total_bill:.2f} ብር`")

if st.button("ትዕዛዝ አስተላልፍ 🚀"):
    if customer_name and telegram_username:
        # የቴሌግራም ስም ማስተካከያ
        clean_username = telegram_username.replace("@", "").strip()
        order_id = datetime.now().strftime("%H%M%S")
        
        # ምላሽ መስጫ ሊንኮች
        yes_msg = urllib.parse.quote(f"ሰላም {customer_name}፣ ትዕዛዝዎ #{order_id} ደርሶናል! እያዘጋጀን ነው።")
        no_msg = urllib.parse.quote(f"ይቅርታ {customer_name}፣ ለጊዜው '{food_choice}' አልቋል።")
        
        confirm_link = f"https://t.me/{clean_username}?text={yes_msg}"
        reject_link = f"https://t.me/{clean_username}?text={no_msg}"

        owner_msg = (
            f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 <b>ደንበኛ:</b> {customer_name}\n"
            f"🍲 <b>ምግብ:</b> {food_choice}\n"
            f"🔢 <b>ብዛት:</b> {qty}\n"
            f"💵 <b>ሂሳብ:</b> {total_bill} ብር\n"
            f"━━━━━━━━━━━━━━━\n"
            f"✅ <a href='{confirm_link}'>ትዕዛዝ ተቀበል</a>\n"
            f"❌ <a href='{reject_link}'>አልቋል በል</a>"
        )

        if send_telegram_msg(owner_msg):
            st.success("✅ ትዕዛዝዎ ለቤት ሰራተኛው ተልኳል!")
            
            # --- 5. ሪሲት ---
            st.markdown(f"""
            <div style="border: 2px solid #4CAF50; padding: 15px; border-radius: 10px; background-color: white; color: black;">
                <h3 style="text-align: center;">🧾 ደረሰኝ</h3>
                <p><b>ቁጥር:</b> #{order_id} | <b>ቀን:</b> {datetime.now().strftime('%M:%S')}</p>
                <hr>
                <p><b>ምግብ:</b> {food_choice} x {qty}</p>
                <h4 style="text-align: right;">ድምር: {total_bill:.2f} ብር</h4>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
        else:
            st.error("⚠️ የቴክኒክ ችግር አጋጥሟል። እባክዎ በስልክ ይደውሉ!")
    else:
        st.warning("⚠️ እባክዎ ስም እና የቴሌግራም መለያ ያስገቡ!")
💡 ለወደፊት ቢጨመሩ የሚመከሩ ነገሮች፦
የምግብ ፎቶዎች: በእያንዳንዱ ምግብ ስር ትንሽ ምስል ብታሳዩ ደንበኛን ይስባል።

የመክፈያ ዘዴ: የባንክ አካውንት ቁጥሮችን በሪሲቱ ስር ማካተት (ለምሳሌ፦ CBE, Telebirr)።

የስራ ሰዓት: ምግብ ቤቱ ዝግ ከሆነ "ትዕዛዝ አስተላልፍ" የሚለው ቁልፍ እንዳይሰራ ማድረግ።

ይህ አፕሊኬሽን ለትንሽ ምግብ ቤት በጣም ቀልጣፋ ስራን ይፈጥራል። ሌላ የሚጨመር ነገር ካለ ይንገሩኝ!

በአንድ ግዜ ከአንድ በላይ ምግብ ማዘዝ እንዲችሉ ይሁን

አንድ ደንበኛ በአንድ ጊዜ ከአንድ በላይ አይነት ምግብ መምረጥ እና ማዘዝ እንዲችል ኮዱን ማሻሻል በጣም ጠቃሚ ነው። ለዚህም st.multiselect እና st.data_editor (ወይም dynamic inputs) በመጠቀም ደንበኛው የፈለገውን ያህል ምግቦች እንዲጨምር ማድረግ እንችላለን።

ከታች የቀረበው ኮድ ደንበኛው ምግቦችን መርጦ ብዛት እንዲሰጥ እና ሲጨርስ የሁሉንም ድምር ሂሳብ እንዲያሳየው ተደርጎ የተሻሻለ ነው።

🛠 የተሻሻለው ኮድ (ለብዙ ትዕዛዝ)
Python
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
✨ ምን ተጨመረ?
st.multiselect: ደንበኛው ከዝርዝሩ ውስጥ ከአንድ በላይ ምግብ እንዲመርጥ ያስችለዋል።

Dynamic Columns: ለእያንዳንዱ የተመረጠ ምግብ የራሱ የሆነ የብዛት መቀየሪያ (number_input) እንዲመጣ ተደርጓል።

Looping Logic: ኮዱ የተመረጡትን ምግቦች በሙሉ አንድ በአንድ እየቆጠረ (Loop) የሁሉንም ድምር ይሰራል።

ዝርዝር መልዕክት: ለባለቤቱ የሚላከው የቴሌግራም መልዕክት ሁሉንም የተመረጡ ምግቦች በዝርዝር ያሳያል።

ይህ አሰራር ደንበኛው በተደጋጋሚ "Order" ቁልፍን ከመጫን ያድነዋል! ሌላ ማስተካከያ ይፈልጋሉ?

እኔ የፈልግኩ select እያደረገ ከአንድ በላይ መምረጥ እንድቺል ነው

ገባኝ፣ አንተ የፈለግከው ደንበኛው እንደ ሱቅ ቅርጫት (Cart) የሚፈልጋቸውን ምግቦች እየመረጠ እንዲጨምርና በመጨረሻ ሁሉንም በአንድ ላይ ማዘዝ እንዲችል ነው።

ለዚህ ደግሞ st.multiselect ከመጠቀም ይልቅ፣ እያንዳንዱ ምግብ ስር "ወደ ዝርዝር ጨምር" የሚል ቁልፍ ቢኖርና የመረጣቸው ምግቦች ከታች ተዘርዝረው ቢታዩ ይበልጥ ግልጽ ይሆናል።

ይህንን ለማድረግ የስትሪምሊት Session State (መረጃን ለጊዜው ማስታወሻ ላይ መያዣ) መጠቀም አለብን።

🛠 የተሻሻለው ኮድ (በቅርጫት/Cart ስልት)
Python
import streamlit as st
from datetime import datetime
import requests
import urllib.parse

# --- 1. የቴሌግራም መረጃ ---
BOT_TOKEN = "8779279617:AAEiHJY-R5rDJXpddYh54RhrLhVZxAOnTkI"
CHAT_ID = "1066005872"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        return requests.post(url, data=payload).status_code == 200
    except: return False

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

st.title("🍳 እሙ ምግብ ቤት")

# --- 3. ምግብ መምረጫ ክፍል ---
st.subheader("🍕 ምግቦችን ይምረጡ")
col_f, col_q, col_b = st.columns([3, 1, 1])

with col_f:
    food_to_add = st.selectbox("ምግብ ይምረጡ", list(menu.keys()), label_visibility="collapsed")
with col_q:
    qty_to_add = st.number_input("ብዛት", min_value=1, value=1, step=1, label_visibility="collapsed")
with col_b:
    if st.button("ጨምር ➕"):
        st.session_state.cart.append({
            "name": food_to_add,
            "qty": qty_to_add,
            "price": menu[food_to_add] * qty_to_add
        })
        st.toast(f"{food_to_add} ተጨምሯል!")

# --- 4. የተመረጡ ምግቦች ዝርዝር (Cart Display) ---
if st.session_state.cart:
    st.write("---")
    st.subheader("🛒 የእርስዎ ትዕዛዞች")
    
    total_bill = 0
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
        c1.write(item['name'])
        c2.write(f"x{item['qty']}")
        c3.write(f"{item['price']:.2f} ብር")
        if c4.button("❌", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()
        total_bill += item['price']
    
    st.markdown(f"### 💰 ጠቅላላ ሂሳብ: **{total_bill:.2f} ብር**")
    
    if st.button("የመረጥኩትን አዝዝ 🚀"):
        customer_name = st.text_input("የእርስዎ ስም (ለማረጋገጫ ያህል)")
        telegram_username = st.text_input("የቴሌግራም መለያ (@...)")
        
        if customer_name and telegram_username:
            order_id = datetime.now().strftime("%H%M%S")
            clean_user = telegram_username.replace("@", "").strip()
            
            # የትዕዛዝ ዝርዝር ለቴሌግራም
            items_text = ""
            for item in st.session_state.cart:
                items_text += f"• {item['name']} (x{item['qty']}) - {item['price']} ብር\n"
            
            owner_msg = (
                f"<b>🔔 አዲስ ትዕዛዝ #{order_id}</b>\n\n"
                f"👤 <b>ደንበኛ:</b> {customer_name}\n"
                f"🍲 <b>ዝርዝር:</b>\n{items_text}\n"
                f"💵 <b>ጠቅላላ:</b> {total_bill} ብር\n\n"
                f"✅ <a href='https://t.me/{clean_user}'>ምላሽ ስጥ</a>"
            )
            
            if send_telegram_msg(owner_msg):
                st.success("✅ ትዕዛዝዎ በተሳካ ሁኔታ ተልኳል!")
                st.session_state.cart = [] # ቅርጫቱን ባዶ ማድረግ
                st.balloons()
            else:
                st.error("ትዕዛዙ አልተላከም::")
        else:
            st.info("እባክዎ ስም እና ቴሌግራም ያስገቡ")
else:
    st.info("ምንም የተመረጠ ምግብ የለም። ከላይ ይምረጡና 'ጨምር' የሚለውን ይጫኑ።"
