import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

INVOICE_DIR = "invoices"

def generate_invoice_pdf(invoice_data: dict) -> tuple[bytes, str]:
    """
    Generates a professional PDF invoice for a POS sale, auto-saves it to PC (invoices/ directory),
    and returns (pdf_bytes, file_path).
    """
    os.makedirs(INVOICE_DIR, exist_ok=True)
    
    first_item = invoice_data["items"][0] if invoice_data.get("items") else {"trans_id": "T10001"}
    main_trans_id = first_item.get("trans_id", "T10001")
    filename = f"Invoice_{main_trans_id}.pdf"
    file_path = os.path.join(INVOICE_DIR, filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'InvTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#18181b'),
        alignment=1
    )

    sub_style = ParagraphStyle(
        'InvSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#64748b'),
        alignment=1
    )

    meta_style = ParagraphStyle(
        'InvMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#334155')
    )

    right_meta_style = ParagraphStyle(
        'InvRightMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#334155'),
        alignment=2
    )

    elements = []

    # Title & Header
    elements.append(Paragraph('SIMS ENTERPRISE', title_style))
    elements.append(Paragraph('Stock & Inventory Management System — Official Sales Receipt', sub_style))
    elements.append(Spacer(1, 14))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#eab308'), spaceAfter=14))

    # Metadata Block
    left_meta = f"<b>Invoice Ref:</b> {main_trans_id}<br/><b>Date & Time:</b> {invoice_data.get('date')} {invoice_data.get('time')}"
    right_meta = f"<b>Cashier ID:</b> {invoice_data.get('sold_by')}<br/><b>Total Line Items:</b> {len(invoice_data.get('items', []))}"
    
    meta_table_data = [
        [Paragraph(left_meta, meta_style), Paragraph(right_meta, right_meta_style)]
    ]
    meta_table = Table(meta_table_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 16))

    # Itemized Table
    headers = ['Trans ID', 'Item Description', 'Qty', 'Unit Price', 'Total ($)']
    rows = [headers]

    for item in invoice_data.get("items", []):
        rows.append([
            str(item["trans_id"]),
            str(item["product_name"]),
            str(item["quantity"]),
            f"${float(item['unit_price']):.2f}",
            f"${float(item['item_total']):.2f}"
        ])

    item_table = Table(rows, colWidths=[80, 230, 50, 90, 90])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#18181b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#eab308')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 14))

    # Grand Total Banner
    grand_total_val = invoice_data.get("grand_total", 0.0)
    total_text = f"<b>GRAND TOTAL:</b> <font size=14 color='#eab308'>${grand_total_val:,.2f}</font>"
    total_p = Paragraph(total_text, ParagraphStyle('TotalP', fontName='Helvetica-Bold', fontSize=12, alignment=2, textColor=colors.white))
    
    total_table = Table([[total_p]], colWidths=[540])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#18181b')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 24))

    # Footer
    footer_text = "Thank you for your business! • SIMS Stock & Inventory Management System"
    elements.append(Paragraph(footer_text, ParagraphStyle('Foot', fontName='Helvetica-Oblique', fontSize=9, alignment=1, textColor=colors.HexColor('#94a3b8'))))

    doc.build(elements)

    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    return pdf_bytes, file_path


def generate_barcode_catalog_pdf(products: list) -> tuple[bytes, str]:
    """
    Generates a professional Printable PDF Barcode & QR Code sheet for all products in catalog.
    Saves to 'invoices/SIMS_Product_Barcodes_Catalog.pdf' and returns (pdf_bytes, file_path).
    """
    os.makedirs(INVOICE_DIR, exist_ok=True)
    filename = "SIMS_Product_Barcodes_Catalog.pdf"
    file_path = os.path.join(INVOICE_DIR, filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CatalogTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#18181b'),
        alignment=1
    )

    sub_style = ParagraphStyle(
        'CatalogSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#64748b'),
        alignment=1
    )

    item_style = ParagraphStyle(
        'ItemStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1e293b')
    )

    elements = []

    # Title & Subtitle
    elements.append(Paragraph('SIMS ENTERPRISE', title_style))
    elements.append(Paragraph('Official Printable Product Barcodes & QR Codes Catalog Sheet', sub_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#6366f1'), spaceAfter=14))

    headers = ['Product Description', '2D QR Code', '1D Barcode (Code128)']
    rows = [[
        Paragraph(f'<b>{h}</b>', ParagraphStyle('HStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.white, alignment=0 if idx == 0 else 1))
        for idx, h in enumerate(headers)
    ]]

    from reportlab.graphics.barcode import code128, qr
    from reportlab.graphics.shapes import Drawing

    for p in products:
        p_name = p.get('name', 'Product')
        p_id = p.get('product_id', 'P000')
        p_cat = p.get('category', 'General')
        p_price = float(p.get('price', 0.0))
        p_stock = int(p.get('quantity', 0))

        info_html = (
            f"<b>{p_name}</b><br/>"
            f"<font color='#6366f1'><b>ID: {p_id}</b></font> &bull; Category: {p_cat}<br/>"
            f"Price: <b>${p_price:.2f}</b> &bull; Stock: {p_stock}"
        )
        info_p = Paragraph(info_html, item_style)

        # Generate QR Code
        qr_w = qr.QrCodeWidget(p_id)
        bounds = qr_w.getBounds()
        w, h = bounds[2] - bounds[0], bounds[3] - bounds[1]
        d_qr = Drawing(52, 52, transform=[52.0/w, 0, 0, 52.0/h, 0, 0])
        d_qr.add(qr_w)

        # Generate 1D Code128 Barcode
        d_bc = code128.Code128(p_id, barHeight=24, barWidth=0.95)

        rows.append([info_p, d_qr, d_bc])

    item_table = Table(rows, colWidths=[230, 130, 180])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#18181b')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))

    elements.append(item_table)
    elements.append(Spacer(1, 16))
    footer_text = "SIMS Stock & Inventory Management System • Generated Printable Barcode Sheet"
    elements.append(Paragraph(footer_text, ParagraphStyle('Foot', fontName='Helvetica-Oblique', fontSize=8.5, alignment=1, textColor=colors.HexColor('#94a3b8'))))

    doc.build(elements)

    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    return pdf_bytes, file_path

