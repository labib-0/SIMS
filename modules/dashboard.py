import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_db_connection
import datetime
from utils.animations import load_lottieurl
from streamlit_lottie import st_lottie

def render_dashboard():
    col_lottie, col_title = st.columns([1, 11])
    with col_lottie:
        lottie_chart = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_vnikrcia.json")
        if lottie_chart:
            st_lottie(lottie_chart, height=60, key="dash_lottie")
    with col_title:
        st.title("**Dashboard Overview**")
    
    with get_db_connection() as conn:
        # Load metrics
        products_count = conn.execute("SELECT COUNT(id) FROM products").fetchone()[0]
        inventory_sum = conn.execute("SELECT SUM(current_stock) FROM products").fetchone()[0] or 0
        
        # Low stock count
        low_stock_count = conn.execute("SELECT COUNT(id) FROM products WHERE current_stock <= minimum_stock").fetchone()[0]
        
        # Today's sales
        today = datetime.date.today().strftime('%Y-%m-%d')
        today_sales_data = conn.execute("SELECT SUM(final_amount), COUNT(id) FROM sales WHERE date(sale_date) = ?", (today,)).fetchone()
        today_sales = today_sales_data[0] or 0.0
        today_transactions = today_sales_data[1] or 0
        
        # Monthly sales
        this_month = datetime.date.today().strftime('%Y-%m')
        monthly_sales = conn.execute("SELECT SUM(final_amount) FROM sales WHERE strftime('%Y-%m', sale_date) = ?", (this_month,)).fetchone()[0] or 0.0
        
        # Revenue total
        total_revenue = conn.execute("SELECT SUM(final_amount) FROM sales").fetchone()[0] or 0.0

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", products_count)
    col2.metric("Current Inventory", inventory_sum)
    col3.metric("Low Stock Alerts", low_stock_count, delta_color="inverse")
    col4.metric("Today's Transactions", today_transactions)

    col1, col2, col3 = st.columns(3)
    col1.metric("Today's Revenue", f"${today_sales:,.2f}")
    col2.metric("Monthly Revenue", f"${monthly_sales:,.2f}")
    col3.metric("Total Revenue", f"${total_revenue:,.2f}")
    
    st.divider()

    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.subheader("**Sales Trend (Last 7 Days)**")
            with get_db_connection() as conn:
                query = """
                    SELECT date(sale_date) as Date, SUM(final_amount) as Revenue
                    FROM sales
                    WHERE sale_date >= date('now', '-7 days')
                    GROUP BY date(sale_date)
                    ORDER BY Date ASC
                """
                sales_df = pd.read_sql_query(query, conn)
            
            if not sales_df.empty:
                fig = px.line(sales_df, x="Date", y="Revenue", markers=True, template="plotly_dark")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sales data available for the last 7 days.")

    with col2:
        with st.container(border=True):
            st.subheader("**Inventory Overview by Category**")
            with get_db_connection() as conn:
                query = """
                    SELECT category as Category, SUM(current_stock) as Stock
                    FROM products
                    GROUP BY category
                """
                inv_df = pd.read_sql_query(query, conn)
                
            if not inv_df.empty:
                fig = px.pie(inv_df, names="Category", values="Stock", hole=0.4, template="plotly_dark")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No inventory data available.")
    
    st.divider()
    
    # Recent Transactions
    st.subheader("**Recent Transactions**")
    with get_db_connection() as conn:
        query = """
            SELECT s.invoice_number, s.final_amount, s.sale_date, u.username_encrypted
            FROM sales s
            JOIN users u ON s.user_id = u.id
            ORDER BY s.sale_date DESC LIMIT 5
        """
        recent_df = pd.read_sql_query(query, conn)
        
    if not recent_df.empty:
        # Decrypt usernames for display
        from utils.auth import decrypt_username
        recent_df['Sales Rep'] = recent_df['username_encrypted'].apply(decrypt_username)
        recent_df = recent_df.drop(columns=['username_encrypted'])
        recent_df['final_amount'] = recent_df['final_amount'].apply(lambda x: f"${x:,.2f}")
        recent_df.rename(columns={'invoice_number': 'Invoice No.', 'final_amount': 'Amount', 'sale_date': 'Date'}, inplace=True)
        st.dataframe(recent_df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent transactions.")
