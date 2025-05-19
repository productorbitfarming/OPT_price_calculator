pip install streamlit

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
        with col2:
            qty = st.number_input(f"Qty - {item['name']}", min_value=1, step=1, value=1, key=item["name"])
        item_total = qty * item["price"]
        total_price += item_total
        selected_items.append({"name": item["name"], "qty": qty, "unit_price": item["price"], "total": item_total})

st.markdown("---")
st.write("### Apply Discount")
discount_input = st.text_input("Enter discount (e.g. `10%` or `5000`):")

# Discount logic
discount_value = 0
if discount_input:
    discount_input = discount_input.strip()
    try:
        if discount_input.endswith('%'):
            discount_percent = float(discount_input[:-1])
            discount_value = (discount_percent / 100) * total_price
        else:
            discount_value = float(discount_input)
    except:
        st.warning("Invalid discount input. Please enter like `10%` or `5000`.")

final_price = total_price - discount_value

# Results
st.markdown("---")
st.write("### 🧾 Bill Summary")

if selected_items:
    for i in selected_items:
        st.write(f"{i['name']} (x{i['qty']}) = ₹{i['total']:,.0f}")
    st.write(f"**Subtotal:** ₹{total_price:,.0f}")
    st.write(f"**Discount:** ₹{discount_value:,.0f}")
    st.write(f"**Final Price (After Discount):** ₹{final_price:,.0f}")
else:
    st.info("Please select items to see the bill.")

