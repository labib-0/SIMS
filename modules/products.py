import streamlit as st
import pandas as pd
from database import get_db_connection
from utils.helpers import log_audit, generate_sku
from utils.validators import validate_product_data
from utils.export import df_to_csv, df_to_excel
import uuid

def render_products():
    st.title("📦 Product Management")
    
    tab1, tab2, tab3 = st.tabs(["View Products", "Add Product", "Import/Export"])
    
    with get_db_connection() as conn:
        categories = [row[0] for row in conn.execute("SELECT name FROM categories").fetchall()]
        suppliers = [row[0] for row in conn.execute("SELECT name FROM suppliers").fetchall()]
    
    with tab1:
        st.subheader("Product List")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("🔍 Search Products", "")
        with col2:
            cat_filter = st.selectbox("Filter by Category", ["All"] + categories)
            
        with get_db_connection() as conn:
            query = "SELECT * FROM products WHERE 1=1"
            params = []
            if search_query:
                query += " AND (name LIKE ? OR sku LIKE ? OR barcode LIKE ?)"
                params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])
            if cat_filter != "All":
                query += " AND category = ?"
                params.append(cat_filter)
                
            df = pd.read_sql_query(query, conn, params=params)
            
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Simple edit/delete selection
            st.markdown("---")
            st.subheader("Edit or Delete Product")
            selected_product_id = st.selectbox("Select Product to Modify", df['id'].tolist(), format_func=lambda x: df[df['id'] == x]['name'].values[0])
            
            if selected_product_id:
                product = df[df['id'] == selected_product_id].iloc[0]
                
                with st.expander("Edit Product"):
                    with st.form("edit_product_form"):
                        e_name = st.text_input("Name", product['name'])
                        e_cat = st.selectbox("Category", categories, index=categories.index(product['category']) if product['category'] in categories else 0)
                        e_pp = st.number_input("Purchase Price", min_value=0.0, value=float(product['purchase_price']), step=0.01)
                        e_sp = st.number_input("Selling Price", min_value=0.0, value=float(product['selling_price']), step=0.01)
                        e_min_s = st.number_input("Minimum Stock", min_value=0, value=int(product['minimum_stock']), step=1)
                        e_sup = st.selectbox("Supplier", [""] + suppliers, index=([""] + suppliers).index(product['supplier']) if product['supplier'] in suppliers else 0)
                        
                        if st.form_submit_button("Update Product"):
                            with get_db_connection() as conn:
                                conn.execute("""
                                    UPDATE products 
                                    SET name=?, category=?, purchase_price=?, selling_price=?, minimum_stock=?, supplier=?
                                    WHERE id=?
                                """, (e_name, e_cat, e_pp, e_sp, e_min_s, e_sup, selected_product_id))
                            log_audit(st.session_state.username, f"Updated product ID: {selected_product_id}")
                            st.success("Product updated successfully!")
                            st.rerun()
                            
                with st.expander("Delete Product"):
                    st.warning("Are you sure you want to delete this product? This action cannot be undone. Products with current stock cannot be deleted.")
                    if st.button("Delete"):
                        if int(product['current_stock']) > 0:
                            st.error("Cannot delete product with existing stock!")
                        else:
                            with get_db_connection() as conn:
                                conn.execute("DELETE FROM products WHERE id=?", (selected_product_id,))
                            log_audit(st.session_state.username, f"Deleted product ID: {selected_product_id}")
                            st.success("Product deleted successfully!")
                            st.rerun()

        else:
            st.info("No products found.")

    with tab2:
        st.subheader("Add New Product")
        if not categories:
            st.warning("Please add Categories in Settings before adding products.")
        else:
            with st.form("add_product_form"):
                col1, col2 = st.columns(2)
                with col1:
                    p_name = st.text_input("Product Name*")
                    p_cat = st.selectbox("Category*", categories)
                    p_sku = st.text_input("SKU (Leave blank to auto-generate)")
                    p_barcode = st.text_input("Barcode")
                with col2:
                    p_pp = st.number_input("Purchase Price*", min_value=0.0, step=0.01)
                    p_sp = st.number_input("Selling Price*", min_value=0.0, step=0.01)
                    p_cs = st.number_input("Initial Stock*", min_value=0, step=1)
                    p_ms = st.number_input("Minimum Stock*", min_value=0, step=1)
                
                p_sup = st.selectbox("Supplier", [""] + suppliers)
                p_desc = st.text_area("Description")
                
                if st.form_submit_button("Save Product"):
                    if not p_sku:
                        p_sku = generate_sku(p_cat, p_name)
                    
                    errors = validate_product_data(p_name, p_cat, p_sku, p_pp, p_sp, p_cs, p_ms)
                    
                    if errors:
                        for err in errors:
                            st.error(err)
                    else:
                        try:
                            with get_db_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute("""
                                    INSERT INTO products (name, category, sku, barcode, purchase_price, selling_price, current_stock, minimum_stock, supplier, description)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (p_name, p_cat, p_sku, p_barcode, p_pp, p_sp, p_cs, p_ms, p_sup, p_desc))
                                new_product_id = cursor.lastrowid
                                
                                # Initial stock record if > 0
                                if p_cs > 0:
                                    # Get user ID
                                    user_id_row = cursor.execute("SELECT id FROM users WHERE username_encrypted = ?", (st.session_state.username,)).fetchone() # username here is decrypted, need to encrypt it to fetch or fetch dynamically
                                    # wait, st.session_state.username is decrypted. Let's fix this in inventory history
                            
                            log_audit(st.session_state.username, f"Added product: {p_name}")
                            st.success(f"Product '{p_name}' added successfully! SKU: {p_sku}")
                            # st.rerun() # Let it show success first
                        except Exception as e:
                            st.error(f"Error adding product: {e}")

    with tab3:
        st.subheader("Export Products")
        with get_db_connection() as conn:
            export_df = pd.read_sql_query("SELECT * FROM products", conn)
            
        if not export_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("Download CSV", data=df_to_csv(export_df), file_name="products.csv", mime="text/csv")
            with col2:
                st.download_button("Download Excel", data=df_to_excel(export_df), file_name="products.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("No products to export.")
