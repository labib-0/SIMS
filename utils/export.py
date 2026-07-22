import pandas as pd
import io
from fpdf import FPDF
import datetime

def df_to_csv(df: pd.DataFrame) -> bytes:
    """Convert dataframe to CSV bytes."""
    return df.to_csv(index=False).encode('utf-8')

def df_to_excel(df: pd.DataFrame) -> bytes:
    """Convert dataframe to Excel bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def df_to_pdf(df: pd.DataFrame, title: str = "Report") -> bytes:
    """Convert dataframe to a simple PDF table."""
    pdf = FPDF(orientation='L') # Landscape for tables
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt=f"{title} - {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("Arial", size=10, style='B')
    if len(df.columns) > 0:
        col_width = pdf.w / (len(df.columns) + 1)
        for col in df.columns:
            pdf.cell(col_width, 10, str(col)[:15], border=1)
        pdf.ln()
        
        # Table Rows
        pdf.set_font("Arial", size=9)
        for index, row in df.iterrows():
            for item in row:
                pdf.cell(col_width, 10, str(item)[:15], border=1)
            pdf.ln()
            
    return pdf.output(dest='S').encode('latin-1')

def generate_invoice_pdf(sale_details, items_df) -> bytes:
    """Generate a printable invoice PDF."""
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", size=16, style='B')
    pdf.cell(200, 10, txt="INVOICE", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Invoice No: {sale_details['invoice_number']}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {sale_details['sale_date']}", ln=True)
    pdf.ln(10)
    
    # Items
    pdf.set_font("Arial", size=10, style='B')
    pdf.cell(80, 10, "Product", border=1)
    pdf.cell(30, 10, "Qty", border=1)
    pdf.cell(40, 10, "Unit Price", border=1)
    pdf.cell(40, 10, "Total", border=1)
    pdf.ln()
    
    pdf.set_font("Arial", size=10)
    for index, row in items_df.iterrows():
        pdf.cell(80, 10, str(row['Product Name'])[:30], border=1)
        pdf.cell(30, 10, str(row['Quantity']), border=1)
        pdf.cell(40, 10, f"${float(row['Unit Price']):.2f}", border=1)
        pdf.cell(40, 10, f"${float(row['Total Price']):.2f}", border=1)
        pdf.ln()
        
    pdf.ln(10)
    
    # Totals
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(150, 10, "Subtotal:", align='R')
    pdf.cell(40, 10, f"${float(sale_details['total_amount']):.2f}", ln=True)
    
    pdf.cell(150, 10, "Tax:", align='R')
    pdf.cell(40, 10, f"${float(sale_details['tax_amount']):.2f}", ln=True)
    
    pdf.cell(150, 10, "Discount:", align='R')
    pdf.cell(40, 10, f"${float(sale_details['discount_amount']):.2f}", ln=True)
    
    pdf.cell(150, 10, "Final Amount:", align='R')
    pdf.cell(40, 10, f"${float(sale_details['final_amount']):.2f}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')
