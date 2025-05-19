import streamlit as st

# Table data
items = [
    {"name": "12 HP PT Pro incl Dead Weight", "price": 168000},
    {"name": "Battery Sets", "price": 67200},
    {"name": "Fast Chargers", "price": 6720},
    {"name": "1 Set of Sugarcane Blades (Weeding) incl. Extended Shaft", "price": 5040},
    {"name": "1 Set of Sugarcane Blades (Earthing-up) incl. Extended Shaft", "price": 5040},
    {"name": "1 Set of Tyres (5x10)", "price": 8400},
    {"name": "Toolkit: Spanner, Gloves, Gum Boots", "price": 1680},
    {"name": "Ginger Kit", "price": 11200},
    {"name": "Seat", "price": 7840},
    {"name": "Jack", "price": 1680}
]

st.title("🌾 Orbit Agritech Equipment Calculator")

st.write("### Select items and enter quantity:")

selected_items = []
total_price = 0

for item in items:
    col1, col2 = st.columns([2, 1])
    with col1:
        checked = st.checkbox(item["name"])
    
    if checked:
        # Set custom minimum quantity for specific items
        min_qty = 1
        default_qty = 1

        if item["name"] == "Fast Chargers":
            min_qty = 2
            default_qty = 2
        elif item["name"] == "12 HP PT Pro incl Dead Weight":
            min_qty = 1
            default_qty = 1

        with col2:
            qty = st.number_input(
                f"Qty - {item['name']}",
                min_value=min_qty,
                step=1,
                value=default_qty,
                key=item["name"]
            )
        
        item_total = qty * item["price"]
        total_price += item_total
        selected_items.append({
            "name": item["name"],
            "qty": qty,
            "unit_price": item["price"],
            "total": item_total
        })


st.markdown("---")
st.write("### Apply Discount")

discount_input = st.text_input("Enter discount (e.g. `10%` or `5000`):")

# Discount logic with cap
discount_value = 0
MAX_DISCOUNT = 130000

if discount_input:
    discount_input = discount_input.strip()
    try:
        if discount_input.endswith('%'):
            discount_percent = float(discount_input[:-1])
            discount_value = (discount_percent / 100) * total_price
        else:
            discount_value = float(discount_input)
    except:
        st.warning("Invalid discount input. Use like `10%` or `5000`.")

    if discount_value > MAX_DISCOUNT:
        st.warning(f"Discount capped at ₹{MAX_DISCOUNT:,.0f} or 43% max")
        discount_value = MAX_DISCOUNT

final_price = total_price - discount_value

# ✅ Final Summary Display
st.markdown("---")
st.write("### 🧾 Bill Summary")

if selected_items:
    st.write("**Selected Items:**")
    for i in selected_items:
        st.write(f"- {i['name']} (x{i['qty']})")

    st.write(f"**Subtotal:** ₹{total_price:,.0f}")
    st.write(f"**Discount:** ₹{discount_value:,.0f}")
    st.write(f"**Final Price (After Discount):** ₹{final_price:,.0f}")
else:
    st.info("Please select items to see the bill.")

import pandas as pd
import io

if selected_items:
    df = pd.DataFrame(selected_items)

    df_summary = pd.DataFrame({
    "Description": ["Subtotal", "Discount (Capped)", "Final Price"],
    "Amount": [total_price, discount_value, final_price]})


    st.markdown("### 📥 Download Your Bill")

    # Combine both tables
    combined_df = pd.concat([df, pd.DataFrame([{}]), df_summary], ignore_index=True)

    # Excel download
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        combined_df.to_excel(writer, index=False, sheet_name='Bill')
    st.download_button(
        label="Download Excel Bill",
        data=excel_buffer,
        file_name="Orbit_Bill.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # PDF download (basic via HTML for now)
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Orbit Agritech Bill Summary", ln=True, align="C")
    pdf.ln(10)
    for item in selected_items:
        pdf.cell(200, 10, txt=f"{item['name']} (x{item['qty']}) = ₹{item['total']:,.0f}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Subtotal: ₹{total_price:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"Discount: ₹{discount_value:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"Final Price: ₹{final_price:,.0f}", ln=True)

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    st.download_button(
        label="Download PDF Bill",
        data=pdf_buffer,
        file_name="Orbit_Bill.pdf",
        mime="application/pdf"
    )
