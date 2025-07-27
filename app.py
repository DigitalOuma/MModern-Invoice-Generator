import streamlit as st
from invoice_generator import create_invoice_pdf
import datetime
import tempfile

st.set_page_config(page_title="Modern Invoice Generator", page_icon=":money_with_wings:")

st.title(":money_with_wings: Modern Invoice Generator")

with st.container():
    st.subheader("Sender (Your Info)")
    company_name    = st.text_input("Your Company/Name")
    company_address = st.text_area("Your Address")
    company_email   = st.text_input("Your Email (optional)")
    company_phone   = st.text_input("Your Phone (optional)")
    company_website = st.text_input("Your Website (optional)")

st.divider()

with st.container():
    st.subheader("Recipient (Client Info)")
    client_name    = st.text_input("Client Name")
    client_address = st.text_area("Client Address")
    client_email   = st.text_input("Client Email (optional)")
    client_phone   = st.text_input("Client Phone (optional)")

st.divider()

with st.container():
    st.subheader("Invoice Details")
    invoice_number = st.text_input("Invoice #", value="1001")
    invoice_date   = st.date_input("Invoice Date", value=datetime.date.today())
    due_date       = st.date_input("Due Date (optional)", value=datetime.date.today() + datetime.timedelta(days=15))
    po_number      = st.text_input("PO Number (optional)")

    currency = st.selectbox("Currency", ["EUR", "USD", "GBP", "MAD", "JPY", "CAD", "AUD", "CNY"], index=0)
    company_logo = st.file_uploader("Company Logo (optional)", type=["png", "jpg", "jpeg"])

st.divider()

with st.container():
    st.subheader("Invoice Items")
    if "items" not in st.session_state:
        st.session_state["items"] = []

    with st.form(key="add_item_form", clear_on_submit=True):
        desc = st.text_input("Description")
        qty = st.number_input("Quantity", min_value=1, value=1, step=1)
        price = st.number_input("Unit Price", min_value=0.00, value=0.00, step=0.01, format="%.2f")
        tax = st.number_input("Item Tax (%)", min_value=0.0, value=0.0, step=0.01, format="%.2f")
        add_item = st.form_submit_button("Add New Item")
        if add_item and desc:
            st.session_state["items"].append((desc, qty, price, tax))

    if st.session_state["items"]:
        st.table([
            {
                "Description": i[0],
                "Qty": i[1],
                "Unit Price": f"{currency} {i[2]:.2f}",
                "Tax (%)": f"{i[3]:.2f}",
                "Total": f"{currency} {(i[1] * i[2]) * (1 + (i[3] / 100)):.2f}",
            }
            for i in st.session_state["items"]
        ])
        if st.button("Clear All Items"):
            st.session_state["items"] = []

st.divider()

st.subheader("Other")
terms = st.text_area("Terms & Conditions (optional)", value="Payment is due within 15 days")
notes = st.text_area("Additional Notes (optional)", value="")
signature = st.file_uploader("Add Your Signature (optional)", type=["png", "jpg", "jpeg"])

st.divider()

if st.button("Generate & Download Invoice PDF"):
    if not company_name or not client_name or not st.session_state["items"]:
        st.warning("Please fill in at least your name, the client name, and add at least one item.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tf:
            logo_bytes = company_logo.read() if company_logo else None
            signature_bytes = signature.read() if signature else None

            create_invoice_pdf(
                company_name=company_name,
                company_address=company_address,
                company_email=company_email,
                company_phone=company_phone,
                company_website=company_website,
                client_name=client_name,
                client_address=client_address,
                client_email=client_email,
                client_phone=client_phone,
                invoice_number=invoice_number,
                invoice_date=str(invoice_date),
                due_date=str(due_date) if due_date else "",
                po_number=po_number,
                items=st.session_state["items"],
                currency=currency,
                terms=terms,
                notes=notes,
                signature_bytes=signature_bytes,
                file_path=tf.name,
                logo_bytes=logo_bytes
            )
            st.success("Invoice generated successfully!")
            with open(tf.name, "rb") as file:
                st.download_button(
                    label=f"Download Invoice PDF ({currency})",
                    data=file,
                    file_name=f"Invoice_{invoice_number}.pdf",
                    mime="application/pdf"
                )