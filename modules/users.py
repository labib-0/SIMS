import streamlit as st
import pandas as pd
from database import get_db_connection
from utils.auth import encrypt_username, decrypt_username, hash_password
from utils.helpers import log_audit
from utils.validators import is_valid_password
from config import ROLES
import datetime

def render_users():
    st.title("👥 User Management")
    
    # Only Admins should access this, but role check is done in app.py. 
    # Just in case:
    if st.session_state.user_role != "Admin":
        st.error("Access Denied. Only Admins can manage users.")
        return
        
    tab1, tab2 = st.tabs(["View Users", "Add New User"])
    
    with tab1:
        st.subheader("System Users")
        with get_db_connection() as conn:
            users_df = pd.read_sql_query("SELECT id, username_encrypted, role, date_of_birth, is_active, created_at FROM users", conn)
            
        if not users_df.empty:
            users_df['Username'] = users_df['username_encrypted'].apply(decrypt_username)
            users_df = users_df.drop(columns=['username_encrypted'])
            users_df['Status'] = users_df['is_active'].apply(lambda x: "Active" if x == 1 else "Inactive")
            display_df = users_df[['id', 'Username', 'role', 'date_of_birth', 'Status', 'created_at']]
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("Manage User")
            selected_user_id = st.selectbox("Select User", users_df['id'].tolist(), format_func=lambda x: users_df[users_df['id'] == x]['Username'].values[0])
            
            if selected_user_id:
                user = users_df[users_df['id'] == selected_user_id].iloc[0]
                
                # Prevent Admin from changing their own role/status here to avoid locking themselves out
                if user['Username'] == st.session_state.username:
                    st.warning("You cannot modify your own account settings here.")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        new_role = st.selectbox("Update Role", ROLES, index=ROLES.index(user['role']))
                        if st.button("Update Role"):
                            with get_db_connection() as conn:
                                conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, selected_user_id))
                            log_audit(st.session_state.username, f"Updated role for user {user['Username']} to {new_role}")
                            st.success("Role updated.")
                            st.rerun()
                            
                    with col2:
                        action_text = "Deactivate" if user['Status'] == "Active" else "Activate"
                        new_status = 0 if user['Status'] == "Active" else 1
                        if st.button(f"{action_text} User"):
                            with get_db_connection() as conn:
                                conn.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, selected_user_id))
                            log_audit(st.session_state.username, f"{action_text}d user {user['Username']}")
                            st.success(f"User {action_text}d.")
                            st.rerun()
                            
                    with st.expander("Reset Password"):
                        new_pw = st.text_input("New Password", type="password")
                        if st.button("Reset User Password"):
                            if is_valid_password(new_pw):
                                with get_db_connection() as conn:
                                    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_pw), selected_user_id))
                                log_audit(st.session_state.username, f"Admin reset password for {user['Username']}")
                                st.success("Password reset successfully.")
                            else:
                                st.error("Password must be at least 6 chars and contain 1 uppercase, 1 lowercase, and 1 digit.")
                                
                    with st.expander("Delete User"):
                        st.warning("Deleting a user removes them permanently. Deactivating is recommended instead.")
                        if st.button("Permanently Delete User"):
                            with get_db_connection() as conn:
                                conn.execute("DELETE FROM users WHERE id = ?", (selected_user_id,))
                            log_audit(st.session_state.username, f"Deleted user {user['Username']}")
                            st.success("User deleted.")
                            st.rerun()

    with tab2:
        st.subheader("Create New User")
        with st.form("new_user_form"):
            new_username = st.text_input("Username*")
            new_password = st.text_input("Password*", type="password")
            new_role = st.selectbox("Role*", ROLES)
            new_dob = st.date_input("Date of Birth*", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
            
            if st.form_submit_button("Create User"):
                if len(new_username) < 3:
                    st.error("Username must be at least 3 characters.")
                elif not is_valid_password(new_password):
                    st.error("Password must be at least 6 chars and contain 1 uppercase, 1 lowercase, and 1 digit.")
                else:
                    encrypted_username = encrypt_username(new_username)
                    hashed_pw = hash_password(new_password)
                    
                    try:
                        with get_db_connection() as conn:
                            # Check if user exists
                            cursor = conn.cursor()
                            cursor.execute("SELECT id FROM users WHERE username_encrypted = ?", (encrypted_username,))
                            if cursor.fetchone():
                                st.error("Username already exists!")
                            else:
                                cursor.execute("""
                                    INSERT INTO users (username_encrypted, password_hash, role, date_of_birth, is_active)
                                    VALUES (?, ?, ?, ?, 1)
                                """, (encrypted_username, hashed_pw, new_role, str(new_dob)))
                                
                        log_audit(st.session_state.username, f"Created new user: {new_username} ({new_role})")
                        st.success(f"User {new_username} created successfully!")
                    except Exception as e:
                        st.error(f"Error creating user: {e}")
