import streamlit as st
import pandas as pd
from database import get_db_connection

def render_audit():
    st.title("📋 Audit Log")
    
    # Check permissions
    if st.session_state.user_role != "Admin":
        st.error("Access Denied. Only Admins can view audit logs.")
        return
        
    st.write("This log tracks all major actions performed within the system.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        date_filter = st.date_input("Filter by Date", value=None)
    with col2:
        search = st.text_input("Search Action or User")
        
    with get_db_connection() as conn:
        query = "SELECT id, user, date, time, action, ip_address FROM audit_logs WHERE 1=1"
        params = []
        
        if date_filter:
            query += " AND date = ?"
            params.append(str(date_filter))
            
        if search:
            query += " AND (user LIKE ? OR action LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
            
        query += " ORDER BY id DESC LIMIT 500" # Limit to prevent slow down
        
        audit_df = pd.read_sql_query(query, conn, params=params)
        
    if not audit_df.empty:
        st.dataframe(audit_df, use_container_width=True, hide_index=True)
        
        # Export option
        from utils.export import df_to_csv
        st.download_button("Export Audit Log (CSV)", data=df_to_csv(audit_df), file_name="audit_logs.csv", mime="text/csv")
    else:
        st.info("No audit logs found matching criteria.")
