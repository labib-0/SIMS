import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_db_connection
from utils.export import df_to_csv, df_to_excel, df_to_pdf
from utils.auth import decrypt_username

def render_reports():
    st.title("📈 Reports & Analytics")
    
    report_type = st.selectbox("Select Report Type", ["Sales Report", "Inventory Report", "Top Selling Products"])
    
    if report_type == "Sales Report":
        st.subheader("Sales Report")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
            
        with get_db_connection() as conn:
            query = """
                SELECT s.invoice_number, s.total_amount, s.tax_amount, s.discount_amount, s.final_amount, s.sale_date, u.username_encrypted
                FROM sales s
                JOIN users u ON s.user_id = u.id
                WHERE date(s.sale_date) BETWEEN ? AND ?
                ORDER BY s.sale_date DESC
            """
            sales_df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            
        if not sales_df.empty:
            sales_df['Sales Rep'] = sales_df['username_encrypted'].apply(decrypt_username)
            sales_df = sales_df.drop(columns=['username_encrypted'])
            
            st.dataframe(sales_df, use_container_width=True, hide_index=True)
            
            total_rev = sales_df['final_amount'].sum()
            st.success(f"Total Revenue for period: ${total_rev:,.2f}")
            
            # Chart
            sales_df['Date'] = pd.to_datetime(sales_df['sale_date']).dt.date
            daily_sales = sales_df.groupby('Date')['final_amount'].sum().reset_index()
            fig = px.line(daily_sales, x="Date", y="final_amount", title="Daily Revenue")
            st.plotly_chart(fig, use_container_width=True)
            
            export_buttons(sales_df, "Sales_Report")
        else:
            st.info("No sales found for the selected period.")
            
    elif report_type == "Inventory Report":
        st.subheader("Inventory Status")
        
        with get_db_connection() as conn:
            query = "SELECT name, category, sku, purchase_price, selling_price, current_stock, minimum_stock FROM products"
            inv_df = pd.read_sql_query(query, conn)
            
        if not inv_df.empty:
            inv_df['Status'] = inv_df.apply(lambda x: 'Low Stock' if x['current_stock'] <= x['minimum_stock'] else 'OK', axis=1)
            inv_df['Total Value'] = inv_df['current_stock'] * inv_df['purchase_price']
            
            st.dataframe(inv_df, use_container_width=True, hide_index=True)
            
            total_value = inv_df['Total Value'].sum()
            st.info(f"Total Inventory Value (Cost): ${total_value:,.2f}")
            
            fig = px.bar(inv_df, x="name", y="current_stock", color="Status", title="Current Stock Levels by Product")
            st.plotly_chart(fig, use_container_width=True)
            
            export_buttons(inv_df, "Inventory_Report")
        else:
            st.info("No inventory data.")
            
    elif report_type == "Top Selling Products":
        st.subheader("Top Selling Products")
        
        with get_db_connection() as conn:
            query = """
                SELECT p.name, p.category, SUM(si.quantity) as Total_Sold, SUM(si.total_price) as Revenue
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                GROUP BY p.id
                ORDER BY Total_Sold DESC
                LIMIT 10
            """
            top_df = pd.read_sql_query(query, conn)
            
        if not top_df.empty:
            st.dataframe(top_df, use_container_width=True, hide_index=True)
            
            fig = px.bar(top_df, x="name", y="Total_Sold", title="Top 10 Products by Quantity Sold")
            st.plotly_chart(fig, use_container_width=True)
            
            export_buttons(top_df, "Top_Selling_Products")
        else:
            st.info("No sales data available.")

def export_buttons(df, filename_prefix):
    st.write("Export:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("CSV", data=df_to_csv(df), file_name=f"{filename_prefix}.csv", mime="text/csv")
    with col2:
        st.download_button("Excel", data=df_to_excel(df), file_name=f"{filename_prefix}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col3:
        st.download_button("PDF", data=df_to_pdf(df, title=filename_prefix.replace('_', ' ')), file_name=f"{filename_prefix}.pdf", mime="application/pdf")
