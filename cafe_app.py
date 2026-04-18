st.markdown("### 🍱 የጋራ ማዕድ (በአንድ እቃ)")

# 1. ምግቦቹን እንዲመርጡ መፍቀድ
selected_items = st.multiselect(
    "በአንድ እቃ እንዲቀላቀሉ የሚፈልጓቸውን ምግቦች ይምረጡ", 
    options=list(menu.keys()),
    help="የመረጧቸው ምግቦች በሙሉ በአንድ ትልቅ ሳህን/እቃ ይቀርባሉ"
)

if selected_items:
    # 2. የዋጋ ስሌት (የመረጧቸው ምግቦች ድምር)
    total_combo_price = sum(menu[item] for item in selected_items)
    st.info(f"የዚህ ጥምረት ጠቅላላ ዋጋ፦ **{total_combo_price:.2f} ብር**")
    
    if st.button("ይህን ጥምረት ወደ ቅርጫት ጨምር 🛒"):
        combo_name = " + ".join(selected_items) # ምግቦቹን በ '+' ያገናኛቸዋል
        st.session_state.cart.append({
            "ምግብ": f"ጥምረት ({combo_name})", 
            "ብዛት": 1, 
            "ዋጋ": total_combo_price,
            "አቀራረብ": "በአንድ እቃ"
        })
        st.success("ጥምረቱ በተሳካ ሁኔታ ተጨምሯል!")
        st.rerun()
