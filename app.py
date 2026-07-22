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
    /* Animated Gradient Background */
    @keyframes gradientBG {{
        0% {{background-position: 0% 50%;}}
        50% {{background-position: 100% 50%;}}
        100% {{background-position: 0% 50%;}}
    }}
    .stApp {{
        background: linear-gradient(-45deg, #000000, #09090b, #171717, #0f172a);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e2e8f0;
    }}
    
    /* Glassmorphism Cards */
    .metric-card, div[data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .metric-card:hover, div[data-testid="stMetric"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.7);
        background: rgba(255, 255, 255, 0.05);
    }}
    
    /* Typography improvements for metrics */
    [data-testid="stMetricValue"] {{
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #cbd5e1 !important;
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6, .markdown-text-container {{
        color: #ffffff !important;
        font-weight: 800 !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
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
