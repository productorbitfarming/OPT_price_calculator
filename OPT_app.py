import streamlit as st

# Set page config
st.set_page_config(page_title="Orbit PT Pro Pricing Calculator", layout="wide")
st.title("🚜 Orbit PT Pro Quotation Calculator")

# Items and pricing list
items = [
    {"name": "12 HP PT Pro incl Dead Weight", "price": 168000},
    {"name": "Battery Sets", "price": 67200},
    {"name": "Fast Chargers", "price": 6720},
    {"name": "1 Set of Sugarcane Blades(Weeding) including Extended Shaft", "price": 5040},
    {"name": "1 Set of Sugarcane Blades(Earthing-up) including Extended Shaft", "price": 5040},
    {"name": "1 Set of Tyres (5x10)", "price": 8400},
    {"name": "Toolkit: Spanner, Gloves, Gum Boots", "price": 1680},
    {"name": "Ginger Kit", "price": 11200},
    {"name": "Seat", "price": 7840},
    {"name": "Jack", "price": 1680},
    {"name": "BuyBack Guarantee", "price": 10000},
]

discount_levels = {
    "L1": {"single": 100000, "double": 130000, "three": 160000},
    "L2": {"single": 110000, "double": 140000, "three": 170000},
    "L3": {"single": 120000, "double": 150000, "three": 180000},
    "L4 (Founder)": {"single": 135000, "double": 165000, "three": 195000}
}

st.write("---")
total_price = 0
selected_items = []

for item in items:
    col1, col2 = st.columns([2, 1])
    with col1:
        checked = st.checkbox(item["name"], help="MRP: ₹10,000 | You Save: 12%" if item["name"] == "BuyBack Guarantee" else None)

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

# Detect battery quantity
battery_qty = 0
for item in selected_items:
    if item["name"] == "Battery Sets":
        battery_qty = item["qty"]
        break

# Discount selection
st.markdown("---")
st.write("### Select Discount Level")
selected_level = st.radio(
    "Choose one of the levels based on offer type:",
    list(discount_levels.keys())
)

discount_type = "single"
if battery_qty == 1:
    discount_type = "single"
elif battery_qty == 2:
    discount_type = "double"
elif battery_qty >= 3:
    discount_type = "three"

discount_value = discount_levels[selected_level][discount_type]
if battery_qty >= 3:
    discount_value += 30000

MAX_DISCOUNT = 150000
if discount_value > MAX_DISCOUNT:
    st.warning(f"Discount capped at ₹{MAX_DISCOUNT:,.0f}")
    discount_value = MAX_DISCOUNT

final_price = total_price - discount_value

# Summary
st.markdown("---")
st.write("### 🧾 Bill Summary")
if selected_items:
    st.write("**Selected Items:**")
    for i in selected_items:
        st.write(f"- {i['name']} (x{i['qty']})")

    st.write(f"**Subtotal:** ₹{total_price:,.0f}")
    st.write(f"**Discount ({selected_level}):** ₹{discount_value:,.0f}")
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
