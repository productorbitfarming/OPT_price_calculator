import streamlit as st

# App Title and Selector
st.set_page_config(page_title="Orbit Docs Generator", layout="wide")
st.title("Orbit Document Generator")

# App Selector
option = st.radio("Select Document Type:", ["Quotation Summary", "Proforma Receipt"])

# ----------------------------------------------------------------------
# Option 1: Quotation Summary
# ----------------------------------------------------------------------
if option == "Quotation Summary":
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    from PIL import Image
    from io import BytesIO

    if "selected_subsidy" not in st.session_state:
        st.session_state.selected_subsidy = 0

    if "form_filled_by" not in st.session_state:
        st.session_state.form_filled_by = ""

    st.subheader("Customer Information")
    customer_name = st.text_input("Customer Name *")
    customer_address = st.text_area("Address *")
    customer_phone = st.text_input("Phone Number *")

    st.subheader("Who is filling this form? *")
    form_filled_by = st.selectbox("Select Role", ["", "Telecaller", "Business Development Officer", "Manager", "Founder"])
    st.session_state.form_filled_by = form_filled_by

    subsidy_caps = {
        "Telecaller": (100000, 130000),
        "Business Development Officer": (110000, 140000),
        "Manager": (120000, 150000),
        "Founder": (155000, 185000),
    }

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

    total_price = 0
    selected_items = []
    battery_qty = 0

    st.markdown("---")
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

            qty = st.number_input(
                f"Qty - {item['name']}",
                min_value=min_qty,
                step=1,
                value=default_qty,
                key=item["name"]
            )
            total_price += qty * item["price"]
            selected_items.append({"name": item["name"], "qty": qty})
            if item["name"] == "Battery Sets":
                battery_qty = qty

    st.markdown("---")
    st.write("### 💸 Subsidy Options")

    apply_subsidy = st.radio("Do you want to apply a Subsidy?", ("No", "Yes"))

    if apply_subsidy == "Yes":
        st.markdown("#### Select Subsidy Amount")
        single_cap, double_cap = subsidy_caps[form_filled_by]
        max_subsidy = single_cap if battery_qty <= 1 else double_cap
        st.slider(
            "Subsidy Slider",
            min_value=0,
            max_value=max_subsidy,
            step=1000,
            key="selected_subsidy"
        )
        st.success(f"Selected Subsidy: ₹{st.session_state.selected_subsidy:,.0f}")
    else:
        st.session_state.selected_subsidy = 0

    selected_subsidy = st.session_state.selected_subsidy
    final_price = total_price - selected_subsidy

    st.markdown("---")
    st.write("### 📟 Bill Summary")

    if selected_items:
        st.table({
            "Item Name": [item["name"] for item in selected_items],
            "Quantity": [item["qty"] for item in selected_items]
        })

        st.write(f"**Total Price:** Rs {total_price:,.0f}")
        st.write(f"**Subsidy Applied:** Rs {selected_subsidy:,.0f}")
        st.write(f"**Subsidized Price (All Inclusive):** Rs {final_price:,.0f}")

        if st.button("📄 Generate Quotation PDF"):
            letterhead_path = "letterpad design_printable (1)_page-0001.jpg"
            img = Image.open(letterhead_path).convert("RGB")
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)

            c.drawImage(ImageReader(img), 0, 0, width=A4[0], height=A4[1])

            y = 660
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(colors.HexColor("#1b4332"))
            c.drawCentredString(300, y, "Quotation Summary")
            y -= 40

            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(50, y, f"Customer Name: {customer_name}")
            y -= 15
            c.drawString(50, y, f"Address: {customer_address}")
            y -= 15
            c.drawString(50, y, f"Phone Number: {customer_phone}")
            y -= 25

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
            c.drawString(50, summary_y - 20, f"Subsidy Applied: Rs {selected_subsidy:,.0f}")
            c.drawString(50, summary_y - 40, f"Subsidized Price (All Inclusive): Rs {final_price:,.0f}")

            c.save()
            pdf_buffer.seek(0)

            st.download_button(
                label="⬇️ Click here to Download PDF Quotation",
                data=pdf_buffer,
                file_name="Orbit_Quotation.pdf",
                mime="application/pdf"
            )
    else:
        st.info("Please select items to see the bill.")

# ----------------------------------------------------------------------
# Option 2: Proforma Receipt
# ----------------------------------------------------------------------
elif option == "Proforma Receipt":
    from docxtpl import DocxTemplate, RichText
    from datetime import datetime

    TEMPLATE_PATH = "Sales Advance Receipt Template.docx"

    st.subheader("Proforma Receipt Generator")

    def numeric_input(label, max_length, key=None):
        val = st.text_input(label, key=key)
        val = ''.join(filter(str.isdigit, val))[:max_length]
        return val

    receipt_no = numeric_input("Receipt Number (max 4 digits)", max_length=4, key="receipt_no")
    date = st.date_input("Date", datetime.today(), key="date").strftime("%d/%m/%Y")
    customer_name = st.text_input("Customer Name", max_chars=50, key="customer_name")
    address = st.text_input("Address", max_chars=200, key="address")
    phone = numeric_input("Phone Number (10 digits)", max_length=10, key="phone")
    email = st.text_input("Email (optional)", max_chars=50, key="email")
    amount_received = st.text_input("Amount Received (₹)", max_chars=10, key="amount_received")

    st.markdown("**Payment Mode:**")
    payment_mode = st.selectbox("", ["Cashfree", "Cash", "Other"], key="payment_mode")

    if payment_mode == "Other":
        custom_payment_mode = st.text_input("Enter Other Payment Mode", key="custom_payment_mode")
        final_payment_mode = custom_payment_mode.strip() if custom_payment_mode else "Other"
    else:
        final_payment_mode = payment_mode

    reference_id = st.text_input("Reference ID (optional)", max_chars=20, key="reference_id")
    payment_date = st.date_input("Date of Payment", datetime.today(), key="payment_date").strftime("%d/%m/%Y")
    balance_due = st.text_input("Balance Due (₹)", max_chars=10, key="balance_due")
    tentative_delivery = st.date_input("Tentative Delivery Date", datetime.today(), key="tentative_delivery").strftime("%d/%m/%Y")

    # Item selection begins AFTER tentative delivery
    st.markdown("---")
    st.subheader("Select Items (No Price — For Annexure Table)")

    items = [
        "12 HP PT Pro incl Dead Weight",
        "Battery Sets",
        "Fast Chargers",
        "1 Set of Sugarcane Blades(Weeding) including Extended Shaft",
        "1 Set of Sugarcane Blades(Earthing-up) including Extended Shaft",
        "1 Set of Tyres (5x10)",
        "Toolkit: Spanner, Gloves, Gum Boots",
        "Ginger Kit",
        "Seat",
        "Jack",
        "BuyBack Guarantee"
    ]

    selected_items = []
    for item in items:
        col1, col2 = st.columns([2, 1])
        with col1:
            checked = st.checkbox(item, key=f"check_{item}")
        if checked:
            qty = st.number_input(f"Qty - {item}", min_value=1, step=1, value=1, key=f"qty_{item}")
            selected_items.append([item, str(qty)])

    if st.button("Generate Receipt DOCX"):
        if not receipt_no:
            st.error("Receipt Number is required and must be numeric up to 4 digits.")
        elif len(phone) != 10:
            st.error("Phone Number must be exactly 10 digits.")
        elif not selected_items:
            st.error("Please select at least one item for the Annexure.")
        else:
            doc = DocxTemplate(TEMPLATE_PATH)

            # Format items table
            table_data = [["Item Name", "Quantity"]]
            table_data.extend(selected_items)

            context = {
                "receipt_no": RichText(receipt_no, bold=True),
                "date": RichText(date, bold=True),
                "customer_name": RichText(customer_name, bold=True),
                "address_line1": RichText(address, bold=True),
                "phone": RichText(phone, bold=True),
                "email": RichText(email if email else "N/A", bold=True),
                "amount_received": RichText(amount_received, bold=True),
                "payment_mode": RichText(final_payment_mode, bold=True),
                "reference_id": RichText(reference_id if reference_id else "N/A", bold=True),
                "payment_date": RichText(payment_date, bold=True),
                "balance_due": RichText(balance_due, bold=True),
                "tentative_delivery": RichText(tentative_delivery, bold=True),
                "items_table": table_data
            }

            output_filename = f"Sales_Advance_Receipt_{receipt_no}.docx"
            doc.render(context)
            doc.save(output_filename)
            st.success(f"Receipt generated: {output_filename}")

            with open(output_filename, "rb") as file:
                st.download_button(
                    label="Download Receipt DOCX",
                    data=file,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
