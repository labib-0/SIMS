import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        /* Import Inter & Outfit Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

        /* Root Global Theme Tokens */
        :root {
            --bg-canvas: #09090b;
            --card-bg: #18181b;
            --card-border: #27272a;
            --accent-gold: #eab308;
            --accent-gold-hover: #facc15;
            --accent-red: #ef4444;
            
            --text-main: #f4f4f5;
            --text-muted: #a1a1aa;
            --text-sub: #71717a;

            --font-sans: 'Inter', -apple-system, sans-serif;
            --font-heading: 'Outfit', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        /* Clean Canvas & Hide Streamlit Default Chrome */
        body, .stApp {
            font-family: var(--font-sans);
            background-color: var(--bg-canvas);
            color: var(--text-main);
        }

        #MainMenu, footer, header {
            visibility: hidden;
            height: 0;
        }

        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 1200px;
        }

        /* Remove default stForm borders & background */
        div[data-testid="stForm"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            box-shadow: none !important;
        }

        /* Ultra-Clean Login Card Wrapper */
        .clean-login-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 40px 36px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
            margin: 0 auto;
            max-width: 440px;
        }

        .clean-login-header {
            text-align: center;
            margin-bottom: 28px;
        }

        .clean-login-title {
            font-family: var(--font-heading);
            font-size: 1.85rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.02em;
            margin: 12px 0 4px 0;
        }

        .clean-login-sub {
            font-size: 0.88rem;
            color: var(--text-muted);
            font-weight: 400;
        }

        /* Input Fields Customization */
        div[data-baseweb="input"] {
            background-color: #09090b !important;
            border: 1px solid #27272a !important;
            border-radius: 12px !important;
            color: #ffffff !important;
            transition: all 0.2s ease !important;
        }

        div[data-baseweb="input"]:focus-within {
            border-color: var(--accent-gold) !important;
            box-shadow: 0 0 0 1px var(--accent-gold) !important;
        }

        input {
            color: #ffffff !important;
            font-size: 0.95rem !important;
        }

        /* Button Styling */
        .stButton > button {
            border-radius: 12px !important;
            font-family: var(--font-sans) !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            height: 44px !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }

        .stButton > button[kind="primary"] {
            background: var(--accent-gold) !important;
            color: #000000 !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(234, 179, 8, 0.25) !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: var(--accent-gold-hover) !important;
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(234, 179, 8, 0.35) !important;
        }

        .stButton > button[kind="secondary"] {
            background: #27272a !important;
            color: #f4f4f5 !important;
            border: 1px solid #3f3f46 !important;
        }

        .stButton > button[kind="secondary"]:hover {
            background: #3f3f46 !important;
            color: #ffffff !important;
        }

        /* Top Bar Control Center Header */
        .sims-top-header {
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 16px;
            padding: 20px 28px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .sims-top-header h1 {
            font-family: var(--font-heading);
            font-size: 1.8rem;
            font-weight: 800;
            color: #ffffff;
            margin: 0;
        }

        /* KPI Metric Cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .clean-kpi-card {
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 16px;
            padding: 20px;
            transition: all 0.2s ease;
        }

        .clean-kpi-card:hover {
            border-color: #3f3f46;
            transform: translateY(-2px);
        }

        .clean-kpi-title {
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 8px;
        }

        .clean-kpi-value {
            font-family: var(--font-heading);
            font-size: 1.8rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 4px;
        }

        .clean-kpi-sub {
            font-size: 0.8rem;
            color: var(--text-sub);
        }

        /* Badges */
        .clean-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
        }

        .clean-badge-green { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
        .clean-badge-yellow { background: rgba(234, 179, 8, 0.15); color: #facc15; }
        .clean-badge-red { background: rgba(239, 68, 68, 0.15); color: #f87171; }
        .clean-badge-orange { background: rgba(249, 115, 22, 0.15); color: #fb923c; }

        /* Kiosk Card */
        .kiosk-card {
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 12px;
            transition: border-color 0.2s ease;
        }

        .kiosk-card:hover {
            border-color: var(--accent-gold);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #09090b;
            border-right: 1px solid #18181b;
        }

        .sidebar-user-card {
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 20px;
        }

        /* Print Media Stylesheet */
        @media print {
            section[data-testid="stSidebar"],
            .sims-top-header,
            header,
            footer,
            .stButton,
            div[data-testid="stForm"] {
                display: none !important;
            }

            body, .stApp {
                background: #ffffff !important;
                color: #000000 !important;
            }

            .printable-invoice {
                box-shadow: none !important;
                border: 1px solid #000000 !important;
                background: #ffffff !important;
                color: #000000 !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

def render_kpi(title: str, value: str, sub: str = ""):
    return f"""
    <div class="clean-kpi-card">
        <div class="clean-kpi-title">{title}</div>
        <div class="clean-kpi-value">{value}</div>
        <div class="clean-kpi-sub">{sub}</div>
    </div>
    """

def render_mcd_kpi(title: str, value: str, sub: str = "", theme: str = "gold"):
    return render_kpi(title, value, sub)

def render_badge(status: str):
    if status == "System Out of Stock":
        return '<span class="clean-badge clean-badge-red">Out of Stock</span>'
    elif status == "System Low Stock":
        return '<span class="clean-badge clean-badge-yellow">Low Stock</span>'
    elif status == "Staff Reported":
        return '<span class="clean-badge clean-badge-orange">Staff Reported</span>'
    else:
        return '<span class="clean-badge clean-badge-green">In Stock</span>'

def render_mcd_badge(status: str):
    return render_badge(status)

def get_category_icon(category: str) -> str:
    cat = category.lower()
    if "grocer" in cat or "food" in cat:
        return "🍔"
    elif "electr" in cat or "tech" in cat:
        return "💻"
    elif "lifestyl" in cat or "beverag" in cat:
        return "🥤"
    elif "furnit" in cat:
        return "🪑"
    elif "home" in cat:
        return "🏠"
    elif "station" in cat or "suppl" in cat:
        return "📦"
    return "📦"

