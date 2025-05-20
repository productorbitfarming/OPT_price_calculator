import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from PIL import Image
import tempfile
import os

# Set page config
st.set_page_config(page_title="Orbit PT Pro Pricing Calculator", layout="wide")
st.title("Orbit PT Pro Quotation Calculator")

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
    {"name": "BuyBack Guarantee", "price": 8929},
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
    st.markdown("#### HIGHER ORBIT AGRITECH PRIVATE LIMITED")
    st.markdown("**Quotation Summary**")

    st.table({
        "Item Name": [item["name"] for item in selected_items],
        "Quantity": [item["qty"] for item in selected_items]
    })

    st.write(f"**Total Price:** ₹{total_price:,.0f}")
    st.write(f"**Discount Applied:** ₹{selected_discount:,.0f}")
    st.write(f"**Discounted Price (All Inclusive):** ₹{final_price:,.0f}")

    # PDF Generation
    if st.button("📄 Download PDF"):
        letterhead_path = "letterpad design-03 (1).jpg"
        img = Image.open(letterhead_path).convert("RGB")
        bg = ImageReader(img)

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(tmp_file.name, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Add space below letterhead
        story.append(Spacer(1, 1.5 * inch))
        story.append(Paragraph("Higher Orbit Agritech Private Limited", styles['Title']))
        story.append(Paragraph("Quotation Summary", styles['Heading2']))
        story.append(Spacer(1, 0.2 * inch))

        # Table with item name and quantity only
        data = [["Item Name", "Quantity"]]
        for item in selected_items:
            data.append([
                item["name"],
                str(item["qty"])
            ])

        table = Table(data, colWidths=[4.5 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3 * inch))

        # Pricing summary
        story.append(Paragraph(f"Total Price: ₹{total_price:,.0f}", styles['Normal']))
        story.append(Paragraph(f"Discount Applied: ₹{selected_discount:,.0f}", styles['Normal']))
        story.append(Paragraph(f"Discounted Price (All Inclusive): ₹{final_price:,.0f}", styles['Normal']))

        # Background drawing
        def add_letterhead(canvas, doc):
            canvas.drawImage(bg, 0, 0, width=A4[0], height=A4[1])

        doc.build(story, onFirstPage=add_letterhead, onLaterPages=add_letterhead)

        with open(tmp_file.name, "rb") as f:
            st.download_button("Download PDF Quotation", f, file_name="Orbit_Quotation.pdf", mime="application/pdf")

        os.unlink(tmp_file.name)

else:
    st.info("Please select items to see the bill.")
