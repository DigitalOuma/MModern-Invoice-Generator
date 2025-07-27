from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

def create_invoice_pdf(
    company_name, company_address, company_email, company_phone, company_website,
    client_name, client_address, client_email, client_phone,
    invoice_number, invoice_date, due_date, po_number,
    items, currency, terms, notes, signature_bytes,
    file_path, logo_bytes=None
):
    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=24)
    styles = getSampleStyleSheet()
    story = []

    # Top: Company Logo and Title
    head_table = []
    logo_img = None
    if logo_bytes:
        logo_img = Image(io.BytesIO(logo_bytes), width=90, height=40)
    left_info = [Paragraph(f'<b>{company_name or ""}</b>', styles['Title'])]
    if company_address: left_info.append(Paragraph(company_address, styles['Normal']))
    if company_email: left_info.append(Paragraph(f"Email: {company_email}", styles['Normal']))
    if company_phone: left_info.append(Paragraph(f"Phone: {company_phone}", styles['Normal']))
    if company_website: left_info.append(Paragraph(f"Website: {company_website}", styles['Normal']))
    if logo_img:
        head_table.append([left_info, logo_img])
    else:
        head_table.append([left_info, ""])
    ht = Table(head_table, colWidths=[390, 110])
    story.append(ht)
    story.append(Spacer(1, 18))

    # Bill To / Invoice Info Row
    info_data = [
        [
            Paragraph('<b>Bill To</b>', styles["Heading4"]), 
            Paragraph('<b>Invoice Info</b>', styles["Heading4"])
        ],
        [
            Paragraph(f'''
                {client_name or ""}<br/>
                {client_address or ""}<br/>
                {(f"Email: {client_email}<br/>" if client_email else "")}
                {(f"Phone: {client_phone}" if client_phone else "")}
            ''', styles["Normal"]),
            Paragraph(f'''
                <b>Invoice #:</b> {invoice_number or ""}<br/>
                <b>Date:</b> {invoice_date or ""}<br/>
                {(f"<b>Due Date:</b> {due_date}<br/>" if due_date else "")}
                {(f"<b>PO #:</b> {po_number}<br/>" if po_number else "")}
            ''', styles["Normal"])
        ]
    ]
    t = Table(info_data, colWidths=[275, 225])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e8f0fa")),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('INNERGRID', (0,1), (-1,-1), 0.25, colors.grey),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#d6eaff")),
        ('BOTTOMPADDING', (0,0), (-1,0), 7),
        ('TOPPADDING', (0,1), (-1,-1), 5)
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    # Items Table
    item_data = [["Description", "Qty", "Unit Price", "Total"]]
    grand_total = 0.0
    for desc, qty, price, tax in items:
        total = (qty * price) * (1 + (float(tax or 0)/100))
        item_data.append([desc, str(qty), f"{currency} {price:,.2f}", f"{currency} {total:,.2f}"])
        grand_total += total
    item_table = Table(item_data, hAlign='LEFT', colWidths=[255, 70, 90, 80])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#b1cdfd")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('BACKGROUND',(0,1),(-1,-1),colors.HexColor("#eef5ff")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0,0), (-1,0), 7),
    ]))
    story.append(item_table)

    # Total
    story.append(Spacer(1, 12))
    total_tbl = Table([
        ["", Paragraph('<b>GRAND TOTAL</b>', styles["Heading4"]), f"{currency} {grand_total:,.2f}"]
    ], colWidths=[255+70, 90, 80])
    total_tbl.setStyle(TableStyle([
        ('BACKGROUND', (1,0), (2,0), colors.HexColor("#3867d6")),
        ('TEXTCOLOR', (1,0), (2,0), colors.whitesmoke),
        ('FONTNAME', (1,0), (2,0), "Helvetica-Bold"),
        ('FONTSIZE', (2,0), (2,0), 14),
        ('ALIGN', (2,0), (2,0), 'CENTER'),
        ('INNERGRID', (0,0), (-1,-1), .25, colors.white),
        ('BOX', (1,0), (2,0), 1, colors.HexColor("#3867d6"))
    ]))
    story.append(total_tbl)

    # Terms & Notes and Signature
    story.append(Spacer(1, 14))
    if terms:
        story.append(Paragraph(f"<b>Terms & Conditions</b>:<br/>{terms}", styles["Normal"]))
    if notes:
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<b>Additional Notes</b>:<br/>{notes}", styles["Normal"]))
    story.append(Spacer(1, 15))
    if signature_bytes:
        sig_img = Image(io.BytesIO(signature_bytes), width=100, height=40)
        story.append(Paragraph("Signed by:", styles['Normal']))
        story.append(sig_img)
        
    story.append(Spacer(1, 18))
    # Thanks message
    styles.add(ParagraphStyle(name='Centered', alignment=1, fontSize=9, textColor=colors.HexColor("#949494")))
    story.append(Paragraph("<i>Thank you for your business!</i>", styles['Centered']))

    doc.build(story)