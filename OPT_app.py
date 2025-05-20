import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from PIL import Image
import tempfile
import os

# Set page config
st.set_page_config(page_title="Orbit PT Pro Pricing Calculator", layout="wide")
st.title("Orbit PT Pro Quotation Calculator")

# Customer information input
st.subheader("Customer Information")
customer_name = st.text_input("Customer Name")
customer_address = st.text_area("Address")
customer_phone = st.text_input("Phone Number")
customer_email = st.text_input("Email (optional)")

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

battery_discount_map = {
    1: [100000, 110000, 120000, 135000],
    2: [130000, 140000, 150000, 165000]
}

st.write("---")
total_price = 0
selected_items = []

for item in items:
    col1, col2 = st.columns([2, 1])
    with col1:
        checked = st.checkbox(item["name"])

    if checked:
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
            "qty": qty
        })

# Detect battery quantity
battery_qty = 0
for item in selected_items:
    if item["name"] == "Battery Sets":
        battery_qty = item["qty"]
        break

# Discount
st.markdown("---")
st.write("### Discount Options")
apply_discount = st.radio("Do you want to apply a discount?", ("No", "Yes"))

if "selected_discount" not in st.session_state:
    st.session_state.selected_discount = 0

if apply_discount == "Yes":
    if battery_qty >= 2:
        applicable_discounts = battery_discount_map[2]
    elif battery_qty == 1:
        applicable_discounts = battery_discount_map[1]
    else:
        applicable_discounts = []

    if applicable_discounts:
        cols = st.columns(len(applicable_discounts))
        for i, val in enumerate(applicable_discounts):
            with cols[i]:
                if st.button(f"₹{val:,.0f}", key=f"discount_{val}"):
                    st.session_state.selected_discount = val
else:
    st.session_state.selected_discount = 0

selected_discount = st.session_state.selected_discount
final_price = total_price - selected_discount

# Bill Summary
st.markdown("---")
st.write("### 📟 Bill Summary")

if selected_items:
    st.markdown("**Quotation Summary**")

    st.table({
        "Item Name": [item["name"] for item in selected_items],
        "Quantity": [item["qty"] for item in selected_items]
    })

    st.write(f"**Total Price:** Rs{total_price:,.0f}")
    st.write(f"**Discount Applied:** Rs{selected_discount:,.0f}")
    st.write(f"**Discounted Price (All Inclusive):** Rs{final_price:,.0f}")

    # PDF Generation
    if st.button("📄 Download PDF"):
        letterhead_path = "letterpad design_printable (1)_page-0001.jpg"
        img = Image.open(letterhead_path).convert("RGB")

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        c = canvas.Canvas(tmp_file.name, pagesize=A4)

        # Set background image
        bg = ImageReader(img)
        c.drawImage(bg, 0, 0, width=A4[0], height=A4[1])

        # Set margin to avoid overlap with header
        y = 660
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.HexColor("#1b4332"))
        c.drawCentredString(300, y, "Quotation Summary")
        y -= 40

        # Customer Info Section
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawString(50, y, f"Customer Name: { customer_name}")
        y -= 15
        c.drawString(50, y, f"Address: { customer_address}")
        y -= 15
        c.drawString(50, y, f"Phone Number: { customer_phone}")
        y -= 15
        if customer_email.strip():
            c.drawString(50, y, f"Email: { customer_email}")
            y -= 15
        else:
            y -= 5

        y -= 10

        # Table (item and quantity)
        data = [["Item Name", "Quantity"]]
        for item in selected_items:
            data.append([item["name"], str(item["qty"])])

        table = Table(data, colWidths=[370, 100])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d6a4f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        table.wrapOn(c, 50, y)
        table.drawOn(c, 50, y - len(data) * 18)

        summary_y = y - len(data) * 18 - 50
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#000000"))
        c.drawString(50, summary_y, f"Total Price: Rs {total_price:,.0f}")
        c.drawString(50, summary_y - 20, f"Discount Applied: Rs {selected_discount:,.0f}")
        c.drawString(50, summary_y - 40, f"Discounted Price (All Inclusive): Rs {final_price:,.0f}")

        c.save()

        with open(tmp_file.name, "rb") as f:
            st.download_button("Download PDF Quotation", f, file_name="Orbit_Quotation.pdf", mime="application/pdf")
        os.unlink(tmp_file.name)
else:
    st.info("Please select items to see the bill.")
