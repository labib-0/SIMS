import streamlit as st
import pandas as pd
from database import get_db_connection
from utils.helpers import log_audit

def render_settings():
    st.title("⚙️ Settings")
    
    tab1, tab2 = st.tabs(["Categories", "Suppliers"])
    
    with tab1:
        st.subheader("Manage Categories")
        with st.form("add_category_form"):
            new_cat = st.text_input("New Category Name")
            if st.form_submit_button("Add Category"):
                if new_cat:
                    try:
                        with get_db_connection() as conn:
                            conn.execute("INSERT INTO categories (name) VALUES (?)", (new_cat.strip(),))
                        log_audit(st.session_state.username, f"Added category: {new_cat}")
                        st.success(f"Category '{new_cat}' added.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding category: {e}")
                else:
                    st.warning("Category name cannot be empty.")
        
        with get_db_connection() as conn:
            cat_df = pd.read_sql_query("SELECT id, name FROM categories", conn)
            
        if not cat_df.empty:
            st.dataframe(cat_df, use_container_width=True, hide_index=True)
        else:
            st.info("No categories defined.")

    with tab2:
        st.subheader("Manage Suppliers")
        with st.form("add_supplier_form"):
            sup_name = st.text_input("Supplier Name")
            sup_contact = st.text_area("Contact Info")
            if st.form_submit_button("Add Supplier"):
                if sup_name:
                    try:
                        with get_db_connection() as conn:
                            conn.execute("INSERT INTO suppliers (name, contact_info) VALUES (?, ?)", (sup_name.strip(), sup_contact.strip()))
                        log_audit(st.session_state.username, f"Added supplier: {sup_name}")
                        st.success(f"Supplier '{sup_name}' added.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding supplier: {e}")
                else:
                    st.warning("Supplier name cannot be empty.")
                    
        with get_db_connection() as conn:
            sup_df = pd.read_sql_query("SELECT id, name, contact_info FROM suppliers", conn)
            
        if not sup_df.empty:
            st.dataframe(sup_df, use_container_width=True, hide_index=True)
        else:
            st.info("No suppliers defined.")
