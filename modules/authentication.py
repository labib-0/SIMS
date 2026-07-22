import streamlit as st
from database import get_db_connection
from utils.auth import encrypt_username, decrypt_username, verify_password, hash_password
from utils.validators import is_valid_password
from utils.helpers import log_audit
from utils.animations import load_lottieurl
from streamlit_lottie import st_lottie
import datetime

def init_session_state():
    """Initialize session state variables for authentication."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    if "show_forgot_password" not in st.session_state:
        st.session_state.show_forgot_password = False

def login_form():
    """Renders the login UI and handles authentication logic."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        lottie_login = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_dn6rwtwl.json")
        if lottie_login:
            st_lottie(lottie_login, height=150, key="login_lottie")
        else:
            st.markdown("<h2 style='text-align: center;'>🔒 SIMS Login</h2>", unsafe_allow_html=True)

    
    if st.session_state.show_forgot_password:
        forgot_password_ui()
        return

    if st.session_state.login_attempts >= 3:
        st.error("Too many failed attempts. Your account is temporarily locked.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Forgot Password", use_container_width=True):
                st.session_state.show_forgot_password = True
                st.rerun()
        with col2:
            if st.button("Try Again", use_container_width=True):
                st.session_state.login_attempts = 0
                st.rerun()
        return

    with st.form("login_form"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)

        if submit:
            if username_input and password_input:
                encrypted_input = encrypt_username(username_input)
                
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE username_encrypted = ? AND is_active = 1", (encrypted_input,))
                    user = cursor.fetchone()

                if user and verify_password(password_input, user["password_hash"]):
                    st.session_state.authenticated = True
                    st.session_state.user_role = user["role"]
                    # Store original username in session
                    st.session_state.username = decrypt_username(user["username_encrypted"])
                    st.session_state.login_attempts = 0
                    log_audit(st.session_state.username, "Login")
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    attempts_left = 3 - st.session_state.login_attempts
                    if attempts_left > 0:
                        st.error(f"Invalid username or password. {attempts_left} attempts remaining.")
                    else:
                        st.rerun()
            else:
                st.warning("Please enter both username and password.")

def forgot_password_ui():
    """UI for forgot password and reset via DOB."""
    st.markdown("### 🔑 Forgot Password")
    st.info("Please verify your identity using your Date of Birth.")
    
    username_input = st.text_input("Username to reset")
    dob_input = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
    
    col1, col2 = st.columns(2)
    with col1:
        verify_btn = st.button("Verify Identity", use_container_width=True)
    with col2:
        if st.button("Back to Login", use_container_width=True):
            st.session_state.show_forgot_password = False
            st.session_state.login_attempts = 0
            st.rerun()
            
    if verify_btn and username_input:
        encrypted_input = encrypt_username(username_input)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, date_of_birth FROM users WHERE username_encrypted = ? AND is_active = 1", (encrypted_input,))
            user = cursor.fetchone()
            
            if user and user["date_of_birth"] == str(dob_input):
                st.session_state.reset_user_id = user["id"]
                st.session_state.reset_username = username_input
                st.success("Identity verified! You may now reset your password.")
            else:
                st.error("Verification failed. Incorrect Username or Date of Birth.")
                
    if "reset_user_id" in st.session_state:
        st.markdown("#### Create New Password")
        with st.form("reset_form"):
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            reset_submit = st.form_submit_button("Reset Password", use_container_width=True)
            
            if reset_submit:
                if not is_valid_password(new_password):
                    st.error("Password must be at least 6 chars and contain 1 uppercase, 1 lowercase, and 1 digit.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    new_hash = hash_password(new_password)
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, st.session_state.reset_user_id))
                    
                    log_audit(st.session_state.reset_username, "Password Reset")
                    st.success("Password reset successfully! You can now login.")
                    # Clean up
                    del st.session_state.reset_user_id
                    del st.session_state.reset_username
                    st.session_state.show_forgot_password = False
                    st.session_state.login_attempts = 0
                    st.rerun()

def logout():
    """Logs the user out."""
    if st.session_state.authenticated:
        log_audit(st.session_state.username, "Logout")
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.session_state.show_forgot_password = False
    st.session_state.login_attempts = 0
    st.rerun()
