import streamlit as st
import os
from config import APP_NAME, PAGE_ICON, THEME_COLOR
from database import init_db
from modules.authentication import init_session_state, login_form, logout
from modules.dashboard import render_dashboard
from modules.products import render_products
from modules.inventory import render_inventory
from modules.sales import render_sales
from modules.reports import render_reports
from modules.users import render_users
from modules.backup import render_backup
from modules.audit import render_audit
from modules.settings import render_settings

# Page Configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Dashboard look
st.markdown(f"""
    <style>
    .stApp {{
        background-color: var(--background-color);
    }}
    .metric-card {{
        background-color: var(--secondary-background-color);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    /* Quick fix for Streamlit metric styling */
    [data-testid="stMetricValue"] {{
        font-size: 1.8rem;
        color: {THEME_COLOR};
    }}
    </style>
""", unsafe_allow_html=True)

# Initialize Database and Session State
init_db()
init_session_state()

def main():
    if not st.session_state.authenticated:
        # Centered login form
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            logo_path = os.path.join("assets", "logo.png")
            if os.path.exists(logo_path):
                st.image(logo_path, use_container_width=True)
            else:
                st.markdown("<h1 style='text-align: center;'>📦 SIMS</h1>", unsafe_allow_html=True)
            login_form()
    else:
        # Sidebar Navigation
        with st.sidebar:
            logo_path = os.path.join("assets", "logo.png")
            if os.path.exists(logo_path):
                st.image(logo_path, width=150)
            st.title("SIMS")
            st.write(f"Welcome, **{st.session_state.username}**")
            st.write(f"Role: *{st.session_state.user_role}*")
            st.divider()
            
            # Role-based menu
            menu_options = ["Dashboard"]
            
            if st.session_state.user_role == "Admin":
                menu_options.extend(["Products", "Inventory", "Sales", "Reports", "Users", "Settings", "Backup & Restore", "Audit Log"])
            elif st.session_state.user_role == "Store Manager":
                menu_options.extend(["Products", "Inventory", "Reports"])
            elif st.session_state.user_role == "Sales Staff":
                menu_options.extend(["Sales", "Products", "Inventory"])
                
            selection = st.radio("Navigation", menu_options)
            
            st.divider()
            if st.button("Logout", use_container_width=True):
                logout()
                
        # Main Content Area
        if selection == "Dashboard":
            render_dashboard()
        elif selection == "Products":
            render_products()
        elif selection == "Inventory":
            render_inventory()
        elif selection == "Sales":
            render_sales()
        elif selection == "Reports":
            render_reports()
        elif selection == "Users":
            render_users()
        elif selection == "Settings":
            render_settings()
        elif selection == "Backup & Restore":
            render_backup()
        elif selection == "Audit Log":
            render_audit()

if __name__ == "__main__":
    main()
