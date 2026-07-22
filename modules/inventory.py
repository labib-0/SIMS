import streamlit as st
import pandas as pd
from database import get_db_connection
from utils.helpers import log_audit
from utils.auth import encrypt_username

def render_inventory():
    st.title("📦 Inventory Management")
    
    tab1, tab2, tab3 = st.tabs(["Current Stock", "Adjust Stock", "Inventory History"])
    
    with tab1:
        st.subheader("Current Stock Levels")
        with get_db_connection() as conn:
            df = pd.read_sql_query("SELECT id, name, sku, category, current_stock, minimum_stock FROM products", conn)
            
        if not df.empty:
            df['Status'] = df.apply(lambda x: '🔴 Low Stock' if x['current_stock'] <= x['minimum_stock'] else '🟢 OK', axis=1)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No products found.")

    with tab2:
        st.subheader("Adjust Stock")
        if not df.empty:
            with st.form("adjust_stock_form"):
                prod_id = st.selectbox("Select Product", df['id'].tolist(), format_func=lambda x: f"{df[df['id'] == x]['name'].values[0]} ({df[df['id'] == x]['sku'].values[0]})")
                adj_type = st.radio("Adjustment Type", ["Stock In", "Stock Out", "Set Exact Stock"])
                qty = st.number_input("Quantity", min_value=1, step=1)
                notes = st.text_input("Notes / Reason")
                
                if st.form_submit_button("Apply Adjustment"):
                    current_stock = int(df[df['id'] == prod_id]['current_stock'].values[0])
                    new_stock = current_stock
                    db_change_type = ""
                    
                    if adj_type == "Stock In":
                        new_stock = current_stock + qty
                        db_change_type = "IN"
                    elif adj_type == "Stock Out":
                        if qty > current_stock:
                            st.error("Cannot subtract more than current stock!")
                            new_stock = -1
                        else:
                            new_stock = current_stock - qty
                            db_change_type = "OUT"
                    elif adj_type == "Set Exact Stock":
                        new_stock = qty
                        db_change_type = "ADJUST"
                        
                    if new_stock >= 0:
                        with get_db_connection() as conn:
                            cursor = conn.cursor()
                            # Get user id
                            user = cursor.execute("SELECT id FROM users WHERE username_encrypted = ?", (encrypt_username(st.session_state.username),)).fetchone()
                            user_id = user[0] if user else 0
                            
                            cursor.execute("UPDATE products SET current_stock = ? WHERE id = ?", (new_stock, prod_id))
                            cursor.execute("""
                                INSERT INTO inventory_history (product_id, change_type, quantity, user_id, notes)
                                VALUES (?, ?, ?, ?, ?)
                            """, (prod_id, db_change_type, qty if adj_type != "Set Exact Stock" else abs(new_stock - current_stock), user_id, notes))
                            
                        prod_name = df[df['id'] == prod_id]['name'].values[0]
                        log_audit(st.session_state.username, f"Adjusted stock for {prod_name}: {adj_type} {qty}")
                        st.success("Stock adjusted successfully!")
                        st.rerun()
        else:
            st.info("Add products first to adjust stock.")

    with tab3:
        st.subheader("Inventory History")
        with get_db_connection() as conn:
            query = """
                SELECT h.date, p.name as Product, h.change_type as Type, h.quantity as Qty, u.username_encrypted, h.notes
                FROM inventory_history h
                JOIN products p ON h.product_id = p.id
                LEFT JOIN users u ON h.user_id = u.id
                ORDER BY h.date DESC
            """
            hist_df = pd.read_sql_query(query, conn)
            
        if not hist_df.empty:
            from utils.auth import decrypt_username
            hist_df['User'] = hist_df['username_encrypted'].apply(decrypt_username)
            hist_df = hist_df.drop(columns=['username_encrypted'])
            st.dataframe(hist_df, use_container_width=True, hide_index=True)
        else:
            st.info("No inventory history.")
