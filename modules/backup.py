import streamlit as st
import os
import shutil
import datetime
from config import DB_PATH, BACKUP_DIR
from database import get_db_connection
from utils.helpers import log_audit
import pandas as pd

def get_file_size(filepath):
    size_bytes = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def render_backup():
    st.title("💾 Database Backup & Restore")
    
    # Check permissions
    if st.session_state.user_role != "Admin":
        st.error("Access Denied. Only Admins can manage backups.")
        return
        
    tab1, tab2 = st.tabs(["Create Backup", "Restore Backup"])
    
    with tab1:
        st.subheader("Create New Backup")
        st.info("Backups are saved locally in the `backups/` directory.")
        
        if st.button("Generate Backup Now", type="primary"):
            try:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_filename = f"sims_backup_{timestamp}.db"
                backup_path = os.path.join(BACKUP_DIR, backup_filename)
                
                shutil.copy2(DB_PATH, backup_path)
                
                size_str = get_file_size(backup_path)
                
                with get_db_connection() as conn:
                    conn.execute("INSERT INTO backup_history (filename, size) VALUES (?, ?)", (backup_filename, size_str))
                    
                log_audit(st.session_state.username, f"Created DB Backup: {backup_filename}")
                st.success(f"Backup created successfully! File: {backup_filename}")
            except Exception as e:
                st.error(f"Failed to create backup: {e}")
                
        st.markdown("---")
        st.subheader("Backup History")
        with get_db_connection() as conn:
            history_df = pd.read_sql_query("SELECT filename as File, date as Date, size as Size FROM backup_history ORDER BY date DESC", conn)
            
        if not history_df.empty:
            st.dataframe(history_df, use_container_width=True, hide_index=True)
            
            # Allow downloading latest backup
            st.markdown("Download a Backup File:")
            selected_file = st.selectbox("Select Backup to Download", history_df['File'].tolist())
            if selected_file:
                file_path = os.path.join(BACKUP_DIR, selected_file)
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        st.download_button("Download Selected Backup", data=f, file_name=selected_file, mime="application/octet-stream")
                else:
                    st.error("File not found on disk.")
        else:
            st.info("No backups found.")

    with tab2:
        st.subheader("Restore Backup")
        st.warning("⚠️ Restoring a backup will overwrite the current database. All data added since the backup will be lost. Ensure you have a recent backup before proceeding.")
        
        backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
        if backups:
            selected_restore = st.selectbox("Select Backup to Restore", backups)
            
            # Confirm checkbox
            confirm = st.checkbox(f"I understand that restoring '{selected_restore}' will overwrite current data.")
            
            if st.button("Restore Database", type="primary", disabled=not confirm):
                try:
                    restore_path = os.path.join(BACKUP_DIR, selected_restore)
                    # Close connections? Streamlit handles connections per request, 
                    # but we should be careful. We are just replacing the file.
                    shutil.copy2(restore_path, DB_PATH)
                    
                    # We can't log to the DB right after overwrite since the log might be gone, 
                    # but we can try to log it to the restored DB.
                    log_audit(st.session_state.username, f"Restored DB from Backup: {selected_restore}")
                    st.success("Database restored successfully! The application might need a restart.")
                    
                    # Force logout to ensure clean state with restored DB
                    st.session_state.authenticated = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to restore backup: {e}")
        else:
            st.info("No backup files found in the backups directory.")
