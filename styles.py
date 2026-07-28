"""
SIMS — styles.py
Full CSS theming system supporting Light & Dark modes.
All styling is injected via st.markdown(unsafe_allow_html=True).
"""
import streamlit as st


# ─────────────────────────────────────────────────────────────
#  THEME TOKENS
# ─────────────────────────────────────────────────────────────

DARK_THEME = {
    "bg_canvas":       "linear-gradient(135deg, #060612 0%, #0c0d24 45%, #100b28 100%)",
    "sidebar_bg":      "#08081a",
    "sidebar_border":  "#1e1b4b",
    "card_bg":         "rgba(14, 14, 28, 0.95)",
    "card_border":     "rgba(99, 102, 241, 0.25)",
    "card_hover":      "rgba(25, 25, 52, 0.95)",
    "card_shadow":     "0 10px 40px rgba(0,0,0,0.5), 0 0 20px rgba(99,102,241,0.12)",
    "accent":          "#818cf8",      # indigo-400
    "accent2":         "#6366f1",      # indigo-500
    "accent3":         "#a78bfa",      # violet-400
    "accent_glow":     "rgba(99,102,241,0.35)",
    "accent_glow2":    "rgba(139,92,246,0.25)",
    "text_main":       "#f1f5f9",
    "text_muted":      "#94a3b8",
    "text_sub":        "#64748b",
    "text_heading":    "#ffffff",
    "input_bg":        "#0a0a1c",
    "input_border":    "#2e2b5e",
    "primary_btn_bg":  "linear-gradient(135deg, #6366f1, #8b5cf6)",
    "primary_btn_text":"#ffffff",
    "secondary_btn_bg":"#1e1b4b",
    "secondary_btn_text":"#a5b4fc",
    "divider":         "#1e1b4b",
    "badge_role_bg":   "rgba(99,102,241,0.2)",
    "badge_role_text": "#a5b4fc",
    "success":         "#4ade80",
    "warning":         "#fbbf24",
    "danger":          "#f87171",
    "info":            "#60a5fa",
    "plotly_paper":    "rgba(0,0,0,0)",
    "plotly_plot":     "rgba(0,0,0,0)",
    "plotly_font":     "#f1f5f9",
    "plotly_grid":     "rgba(99,102,241,0.15)",
    "kpi_gradient":    "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
    "header_bg":       "rgba(14, 14, 28, 0.95)",
    "login_card_bg":   "rgba(14, 14, 28, 0.90)",
    "login_card_border":"rgba(99,102,241,0.35)",
    "glass_blur":      "blur(20px)",
    "table_header":    "#1e1b4b",
    "table_row_alt":   "rgba(99,102,241,0.06)",
}

LIGHT_THEME = {
    "bg_canvas":       "linear-gradient(135deg, #f0f4ff 0%, #e8ecfd 40%, #f5f3ff 100%)",
    "sidebar_bg":      "#ffffff",
    "sidebar_border":  "#e0e7ff",
    "card_bg":         "#ffffff",
    "card_border":     "#e0e7ff",
    "card_hover":      "#f5f3ff",
    "card_shadow":     "0 4px 20px rgba(99,102,241,0.1)",
    "accent":          "#6366f1",      # indigo-500
    "accent2":         "#4f46e5",      # indigo-600
    "accent3":         "#7c3aed",      # violet-600
    "accent_glow":     "rgba(99,102,241,0.15)",
    "accent_glow2":    "rgba(124,58,237,0.1)",
    "text_main":       "#1e1b4b",
    "text_muted":      "#64748b",
    "text_sub":        "#94a3b8",
    "text_heading":    "#0f0a30",
    "input_bg":        "#f8faff",
    "input_border":    "#c7d2fe",
    "primary_btn_bg":  "linear-gradient(135deg,#6366f1,#7c3aed)",
    "primary_btn_text":"#ffffff",
    "secondary_btn_bg":"#ede9fe",
    "secondary_btn_text":"#4f46e5",
    "divider":         "#e0e7ff",
    "badge_role_bg":   "rgba(99,102,241,0.1)",
    "badge_role_text": "#4f46e5",
    "success":         "#16a34a",
    "warning":         "#d97706",
    "danger":          "#dc2626",
    "info":            "#2563eb",
    "plotly_paper":    "rgba(0,0,0,0)",
    "plotly_plot":     "rgba(0,0,0,0)",
    "plotly_font":     "#1e1b4b",
    "plotly_grid":     "rgba(99,102,241,0.12)",
    "kpi_gradient":    "linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)",
    "header_bg":       "rgba(255,255,255,0.95)",
    "login_card_bg":   "rgba(255,255,255,0.85)",
    "login_card_border":"rgba(99,102,241,0.25)",
    "glass_blur":      "blur(20px)",
    "table_header":    "#ede9fe",
    "table_row_alt":   "rgba(99,102,241,0.03)",
}


def get_theme():
    """Returns current theme token dict."""
    if st.session_state.get("theme", "dark") == "light":
        return LIGHT_THEME
    return DARK_THEME


def get_plotly_layout(t: dict = None):
    """Returns a base Plotly layout dict matching the current theme."""
    if t is None:
        t = get_theme()
    return dict(
        paper_bgcolor=t["plotly_paper"],
        plot_bgcolor=t["plotly_plot"],
        font=dict(color=t["plotly_font"], family="Inter, sans-serif", size=12),
        title_font=dict(color=t["plotly_font"], size=14, family="Outfit, sans-serif"),
        xaxis=dict(
            gridcolor=t["plotly_grid"],
            linecolor=t["plotly_grid"],
            zerolinecolor=t["plotly_grid"],
            tickfont=dict(color=t["text_muted"]),
            showgrid=True,
        ),
        yaxis=dict(
            gridcolor=t["plotly_grid"],
            linecolor=t["plotly_grid"],
            zerolinecolor=t["plotly_grid"],
            tickfont=dict(color=t["text_muted"]),
            showgrid=True,
        ),
        legend=dict(
            font=dict(color=t["plotly_font"], size=11),
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        hoverlabel=dict(
            bgcolor=t["card_bg"],
            font_size=12,
            font_color=t["text_main"],
            bordercolor=t["accent"],
        ),
    )


def inject_custom_css():
    t = get_theme()
    is_light = st.session_state.get("theme", "dark") == "light"

    st.markdown(f"""
        <style>
        /* ── Fonts ─────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

        /* ── Root Tokens & Streamlit Core Overrides ──────── */
        :root {{
            --background-color:           {t['bg_canvas']} !important;
            --secondary-background-color: {t['input_bg']} !important;
            --text-color:                 {t['text_main']} !important;
            --primary-color:              {t['accent']} !important;

            --accent:        {t['accent']};
            --accent2:       {t['accent2']};
            --accent3:       {t['accent3']};
            --accent-glow:   {t['accent_glow']};
            --card-bg:       {t['card_bg']};
            --card-border:   {t['card_border']};
            --text-main:     {t['text_main']};
            --text-muted:    {t['text_muted']};
            --text-sub:      {t['text_sub']};
            --font-sans:     'Inter', -apple-system, sans-serif;
            --font-heading:  'Outfit', sans-serif;
            --font-mono:     'JetBrains Mono', monospace;
        }}

        /* ── App Background ──────────────────────────────── */
        .stApp, body, [data-testid="stAppViewContainer"] {{
            font-family: var(--font-sans) !important;
            background: {t['bg_canvas']} !important;
            background-attachment: fixed !important;
            color: {t['text_main']} !important;
        }}

        /* ── Hide Streamlit Chrome (keep toolbar + sidebar toggle) ── */
        #MainMenu, footer {{ visibility: hidden; height: 0; }}

        /* Keep header transparent — toolbar remains accessible */
        header[data-testid="stHeader"] {{
            background: transparent !important;
        }}
        [data-testid="stToolbar"] {{ visibility: visible !important; }}

        /* ── Sidebar collapsed control — styled as a pill button ── */
        [data-testid="collapsedControl"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            background: linear-gradient(135deg, {t['accent2']}, {t['accent3']}) !important;
            border-radius: 0 12px 12px 0 !important;
            top: 120px !important;
            color: white !important;
            box-shadow: 4px 0 18px {t['accent_glow']} !important;
            z-index: 9999 !important;
            width: 32px !important;
            height: 44px !important;
            padding: 0 4px !important;
            transition: all 0.2s ease !important;
        }}
        [data-testid="collapsedControl"]:hover {{
            width: 40px !important;
            box-shadow: 6px 0 28px {t['accent_glow']} !important;
            background: linear-gradient(135deg, {t['accent3']}, {t['accent2']}) !important;
        }}
        [data-testid="collapsedControl"] svg {{
            color: white !important;
            fill: white !important;
        }}

        /* ── Main Container ─────────────────────────────── */
        .block-container {{
            padding-top: 3.5rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 1380px !important;
        }}

        /* ── Chart Card — wraps each dashboard chart ────── */
        .chart-card {{
            background: {t['card_bg']};
            border: 1px solid {t['card_border']};
            border-radius: 18px;
            padding: 20px 18px 14px;
            margin-bottom: 6px;
            box-shadow: {t['card_shadow']};
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }}
        .chart-card:hover {{
            border-color: {t['accent']};
            box-shadow: 0 8px 32px {t['accent_glow']};
        }}

        /* ── Sidebar ─────────────────────────────────────── */
        section[data-testid="stSidebar"] {{
            background: {t['sidebar_bg']} !important;
            border-right: 1px solid {t['sidebar_border']} !important;
            backdrop-filter: blur(20px) !important;
        }}

        section[data-testid="stSidebar"] > div {{
            padding: 1.2rem 1rem !important;
        }}

        /* ── Sidebar Toggle Button (floating) ──────────── */
        .sidebar-reopen-btn {{
            position: fixed;
            top: 80px;
            left: 12px;
            z-index: 9999;
            background: {t['accent2']};
            color: white;
            border: none;
            border-radius: 10px;
            width: 40px;
            height: 40px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 16px {t['accent_glow']};
            transition: all 0.2s ease;
            font-size: 18px;
            line-height: 1;
        }}
        .sidebar-reopen-btn:hover {{
            transform: scale(1.08);
            box-shadow: 0 6px 24px {t['accent_glow']};
        }}

        /* ── Sidebar User Card ──────────────────────────── */
        .sidebar-user-card {{
            background: linear-gradient(135deg, {t['accent2']}22, {t['accent3']}11) !important;
            border: 1px solid {t['card_border']} !important;
            border-radius: 16px !important;
            padding: 16px !important;
            margin-bottom: 20px !important;
        }}

        /* ── Sidebar Nav Buttons ─────────────────────────── */
        section[data-testid="stSidebar"] .stButton > button {{
            border-radius: 10px !important;
            height: 42px !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding-left: 12px !important;
            transition: all 0.18s ease !important;
            border: 1px solid transparent !important;
        }}

        section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
            background: transparent !important;
            color: {t['text_muted']} !important;
        }}

        section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
            background: {t['accent_glow']} !important;
            color: {t['accent']} !important;
            border-color: {t['card_border']} !important;
        }}

        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, {t['accent2']}, {t['accent3']}) !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: 0 4px 14px {t['accent_glow']} !important;
        }}

        /* ── Top Header Bar ─────────────────────────────── */
        .sims-top-header {{
            background: {t['header_bg']};
            border: 1px solid {t['card_border']};
            border-radius: 18px;
            padding: 18px 28px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: {t['glass_blur']};
            box-shadow: {t['card_shadow']};
        }}

        .sims-top-header h1 {{
            font-family: var(--font-heading) !important;
            font-size: 1.6rem !important;
            font-weight: 800 !important;
            color: {t['text_heading']} !important;
            margin: 0 !important;
            background: linear-gradient(135deg, {t['accent']}, {t['accent3']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        /* ── KPI Cards ──────────────────────────────────── */
        .kpi-card {{
            background: {t['card_bg']};
            border: 1px solid {t['card_border']};
            border-radius: 18px;
            padding: 22px 20px;
            position: relative;
            overflow: hidden;
            transition: all 0.25s cubic-bezier(0.16,1,0.3,1);
            box-shadow: {t['card_shadow']};
        }}

        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 4px; height: 100%;
            background: {t['kpi_gradient']};
            border-radius: 4px 0 0 4px;
        }}

        .kpi-card::after {{
            content: '';
            position: absolute;
            top: -40px; right: -40px;
            width: 100px; height: 100px;
            background: {t['accent_glow']};
            border-radius: 50%;
            filter: blur(25px);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-3px);
            border-color: {t['accent']};
            box-shadow: 0 12px 40px {t['accent_glow']}, {t['card_shadow']};
        }}

        .kpi-card:hover::after {{ opacity: 1; }}

        .kpi-icon {{
            width: 40px; height: 40px;
            border-radius: 10px;
            background: {t['accent_glow']};
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 14px;
        }}

        .kpi-title {{
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: {t['text_muted']};
            margin-bottom: 6px;
        }}

        .kpi-value {{
            font-family: var(--font-heading);
            font-size: 1.9rem;
            font-weight: 800;
            color: {t['text_heading']};
            margin-bottom: 4px;
            line-height: 1.1;
        }}

        .kpi-sub {{
            font-size: 0.78rem;
            color: {t['text_sub']};
        }}

        /* ── Generic Cards ──────────────────────────────── */
        .sims-card {{
            background: {t['card_bg']};
            border: 1px solid {t['card_border']};
            border-radius: 18px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: {t['card_shadow']};
            transition: all 0.2s ease;
        }}

        .sims-card:hover {{
            border-color: {t['accent']};
            box-shadow: 0 8px 30px {t['accent_glow']};
        }}

        /* ── Kiosk / Product Cards ─────────────────────── */
        .kiosk-card {{
            background: {t['card_bg']};
            border: 1px solid {t['card_border']};
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 10px;
            transition: all 0.2s ease;
        }}

        .kiosk-card:hover {{
            border-color: {t['accent']};
            background: {t['card_hover']};
            box-shadow: 0 4px 16px {t['accent_glow']};
        }}

        /* ── Badges ─────────────────────────────────────── */
        .badge {{
            display: inline-flex; align-items: center;
            padding: 3px 10px; border-radius: 99px;
            font-size: 0.75rem; font-weight: 600;
        }}

        .badge-indigo  {{ background: {t['badge_role_bg']}; color: {t['badge_role_text']}; }}
        .badge-green   {{ background: rgba(74,222,128,0.12); color: {t['success']}; }}
        .badge-yellow  {{ background: rgba(251,191,36,0.12); color: {t['warning']}; }}
        .badge-red     {{ background: rgba(248,113,113,0.12); color: {t['danger']}; }}
        .badge-blue    {{ background: rgba(96,165,250,0.12); color: {t['info']}; }}

        /* backward compat */
        .clean-badge           {{ display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }}
        .clean-badge-green     {{ background: rgba(74,222,128,0.12); color: {t['success']}; }}
        .clean-badge-yellow    {{ background: rgba(251,191,36,0.12); color: {t['warning']}; }}
        .clean-badge-red       {{ background: rgba(248,113,113,0.12); color: {t['danger']}; }}
        .clean-badge-orange    {{ background: rgba(251,146,60,0.12); color: #fb923c; }}

        /* ── Base Text & Label Colors ───────────────────── */
        label, p, span, h1, h2, h3, h4, h5, h6 {{
            color: {t['text_main']};
        }}
        .stMarkdown {{
            color: {t['text_main']} !important;
        }}
        [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {{
            color: {t['text_main']} !important;
            font-weight: 600 !important;
        }}

        /* ── File Uploader Dropzone (Fixes Black Box in Light Mode) ── */
        div[data-testid="stFileUploader"],
        section[data-testid="stFileUploaderDropzone"],
        [data-testid="stFileUploaderDropzone"] {{
            background-color: {t['input_bg']} !important;
            border: 2px dashed {t['input_border']} !important;
            border-radius: 16px !important;
            color: {t['text_main']} !important;
            padding: 18px !important;
        }}
        section[data-testid="stFileUploaderDropzone"] * {{
            color: {t['text_main']} !important;
            background-color: transparent !important;
        }}
        section[data-testid="stFileUploaderDropzone"] button {{
            background-color: {t['card_bg']} !important;
            border: 1px solid {t['card_border']} !important;
            color: {t['text_main']} !important;
            border-radius: 10px !important;
        }}
        section[data-testid="stFileUploaderDropzone"]:hover {{
            border-color: {t['accent']} !important;
            background-color: {t['card_hover']} !important;
        }}

        /* ── Popovers, Dropdowns & Menus (Baseweb) ─────── */
        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        ul[role="listbox"] {{
            background-color: {t['card_bg']} !important;
            border: 1px solid {t['card_border']} !important;
            border-radius: 12px !important;
            color: {t['text_main']} !important;
            box-shadow: {t['card_shadow']} !important;
        }}
        li[role="option"] {{
            color: {t['text_main']} !important;
            background-color: {t['card_bg']} !important;
        }}
        li[role="option"]:hover, li[aria-selected="true"] {{
            background-color: {t['card_hover']} !important;
            color: {t['accent']} !important;
        }}

        /* ── Dialogs / Modals ──────────────────────────── */
        div[data-testid="stDialog"] > div {{
            background-color: {t['card_bg']} !important;
            border: 1px solid {t['card_border']} !important;
            border-radius: 20px !important;
            color: {t['text_main']} !important;
        }}

        /* ── Inputs ─────────────────────────────────────── */
        div[data-baseweb="input"],
        div[data-baseweb="base-input"] {{
            background-color: {t['input_bg']} !important;
            border: 1px solid {t['input_border']} !important;
            border-radius: 12px !important;
            transition: all 0.2s ease !important;
        }}

        div[data-baseweb="input"]:focus-within {{
            border-color: {t['accent']} !important;
            box-shadow: 0 0 0 2px {t['accent_glow']} !important;
        }}

        input, textarea {{
            color: {t['text_main']} !important;
            font-size: 0.95rem !important;
            background: transparent !important;
        }}

        /* Selectbox & Tags */
        div[data-baseweb="select"] > div {{
            background-color: {t['input_bg']} !important;
            border: 1px solid {t['input_border']} !important;
            border-radius: 12px !important;
            color: {t['text_main']} !important;
        }}
        div[data-baseweb="select"] * {{
            color: {t['text_main']} !important;
        }}
        div[data-baseweb="tag"] {{
            background-color: {t['accent_glow']} !important;
            color: {t['accent']} !important;
            border-radius: 6px !important;
        }}

        /* ── Buttons (global) ───────────────────────────── */
        .stButton > button {{
            border-radius: 12px !important;
            font-family: var(--font-sans) !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            height: 44px !important;
            transition: all 0.22s cubic-bezier(0.16,1,0.3,1) !important;
            letter-spacing: 0.01em !important;
        }}

        .stButton > button[kind="primary"] {{
            background: {t['primary_btn_bg']} !important;
            color: {t['primary_btn_text']} !important;
            border: none !important;
            box-shadow: 0 4px 16px {t['accent_glow']} !important;
        }}

        .stButton > button[kind="primary"]:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 28px {t['accent_glow']} !important;
            filter: brightness(1.1) !important;
        }}

        .stButton > button[kind="secondary"] {{
            background: {t['secondary_btn_bg']} !important;
            color: {t['secondary_btn_text']} !important;
            border: 1px solid {t['card_border']} !important;
        }}

        .stButton > button[kind="secondary"]:hover {{
            background: {t['accent_glow']} !important;
            color: {t['accent']} !important;
            border-color: {t['accent']} !important;
        }}

        /* ── Download button ────────────────────────────── */
        .stDownloadButton > button {{
            border-radius: 12px !important;
            font-weight: 600 !important;
            background: {t['primary_btn_bg']} !important;
            color: {t['primary_btn_text']} !important;
            border: none !important;
        }}

        /* ── Form Container ─────────────────────────────── */
        div[data-testid="stForm"] {{
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            box-shadow: none !important;
        }}

        /* ── Login Page ─────────────────────────────────── */
        .login-wrapper {{
            min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
            background: {t['bg_canvas']};
        }}

        .login-card {{
            background: {t['login_card_bg']};
            border: 1px solid {t['login_card_border']};
            border-radius: 24px;
            padding: 44px 40px;
            box-shadow: 0 32px 80px rgba(0,0,0,0.3), 0 0 0 1px {t['accent_glow']};
            backdrop-filter: {t['glass_blur']};
            max-width: 440px; width: 100%;
            animation: fadeInUp 0.5s ease;
        }}

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(24px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        .login-brand {{
            text-align: center; margin-bottom: 32px;
        }}

        .login-title {{
            font-family: var(--font-heading);
            font-size: 2rem; font-weight: 900;
            background: linear-gradient(135deg, {t['accent']}, {t['accent3']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 14px 0 4px;
        }}

        .login-sub {{
            font-size: 0.88rem; color: {t['text_muted']};
        }}

        /* backward compat */
        .clean-login-title {{
            font-family: var(--font-heading);
            font-size: 1.85rem; font-weight: 800;
            background: linear-gradient(135deg, {t['accent']}, {t['accent3']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 12px 0 4px;
        }}

        .clean-login-sub {{
            font-size: 0.88rem; color: {t['text_muted']};
        }}

        /* ── Tabs ───────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {{
            background: {t['card_bg']} !important;
            border-radius: 12px !important;
            padding: 4px !important;
            border: 1px solid {t['card_border']} !important;
            gap: 2px !important;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px !important;
            font-weight: 600 !important;
            color: {t['text_muted']} !important;
            padding: 8px 16px !important;
            transition: all 0.2s ease !important;
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {t['accent2']}, {t['accent3']}) !important;
            color: #ffffff !important;
        }}

        /* ── Bordered Containers (Chart Cards) ──────────── */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: {t['card_bg']} !important;
            border: 1px solid {t['card_border']} !important;
            border-radius: 18px !important;
            padding: 16px 14px 8px !important;
            box-shadow: {t['card_shadow']} !important;
            transition: all 0.22s ease !important;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            border-color: {t['accent']} !important;
            box-shadow: 0 8px 30px {t['accent_glow']} !important;
        }}

        /* ── DataFrames ─────────────────────────────────── */
        .stDataFrame {{
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid {t['card_border']} !important;
        }}

        /* ── Alerts / Info boxes ────────────────────────── */
        div[data-testid="stAlert"] {{
            border-radius: 12px !important;
            border: 1px solid {t['card_border']} !important;
            background: {t['card_bg']} !important;
            color: {t['text_main']} !important;
        }}

        /* ── Expander ───────────────────────────────────── */
        div[data-testid="stExpander"] {{
            border: 1px solid {t['card_border']} !important;
            border-radius: 14px !important;
            background: {t['card_bg']} !important;
        }}

        /* ── Divider ────────────────────────────────────── */
        hr {{
            border-color: {t['divider']} !important;
            margin: 1.5rem 0 !important;
        }}

        /* ── Section Headers ────────────────────────────── */
        h1, h2, h3, h4 {{
            font-family: var(--font-heading) !important;
            color: {t['text_heading']} !important;
            font-weight: 700 !important;
        }}

        /* subheader rendered by st.subheader */
        [data-testid="stHeading"] h2 {{
            font-size: 1.35rem !important;
            font-weight: 700 !important;
            color: {t['text_heading']} !important;
        }}

        /* ── Caption / Small text ───────────────────────── */
        .stCaption, caption, small {{
            color: {t['text_sub']} !important;
            font-size: 0.78rem !important;
        }}

        /* ── Toast ──────────────────────────────────────── */
        div[data-testid="stToast"] {{
            background: {t['card_bg']} !important;
            border: 1px solid {t['accent']} !important;
            border-radius: 12px !important;
            color: {t['text_main']} !important;
        }}

        /* ── Number Input ───────────────────────────────── */
        div[data-testid="stNumberInput"] input {{
            background: {t['input_bg']} !important;
            border-radius: 10px !important;
        }}

        /* ── Activity Log ───────────────────────────────── */
        .activity-item {{
            padding: 10px 14px;
            border-radius: 10px;
            margin-bottom: 6px;
            background: {t['table_row_alt']};
            border-left: 3px solid {t['accent']};
            font-size: 0.85rem;
            color: {t['text_muted']};
        }}

        .activity-item .ts {{
            font-family: var(--font-mono);
            font-size: 0.8rem;
            color: {t['accent']};
        }}

        /* ── Section Title with Icon ────────────────────── */
        .section-title {{
            display: flex; align-items: center; gap: 10px;
            font-family: var(--font-heading);
            font-size: 1.1rem; font-weight: 700;
            color: {t['text_heading']};
            margin-bottom: 14px;
        }}

        /* ── Notification Badge ─────────────────────────── */
        .notif-badge {{
            background: {t['danger']};
            color: white;
            border-radius: 99px;
            font-size: 0.65rem;
            font-weight: 700;
            padding: 1px 6px;
            display: inline-block;
            vertical-align: middle;
            margin-left: 4px;
            line-height: 1.4;
        }}

        /* ── Status pill inside tables ──────────────────── */
        .pill {{
            display: inline-block;
            padding: 2px 10px; border-radius: 99px;
            font-size: 0.72rem; font-weight: 700;
        }}

        /* ── Scrollbar ──────────────────────────────────── */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: {t['card_border']}; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: {t['accent']}; }}

        /* ── Page transition / Fade-in ──────────────────── */
        .main .block-container {{
            animation: pageFadeIn 0.3s ease;
        }}

        @keyframes pageFadeIn {{
            from {{ opacity: 0.7; transform: translateY(6px); }}
            to   {{ opacity: 1;   transform: translateY(0); }}
        }}

        /* ── Print Receipt (Hides Web App UI, Prints ONLY Invoice Card) ── */
        @media print {{
            html, body, .stApp, [data-testid="stAppViewContainer"], .main, .block-container {{
                background: #ffffff !important;
                color: #0f172a !important;
                padding: 0 !important;
                margin: 0 !important;
            }}
            body * {{
                visibility: hidden !important;
            }}
            section[data-testid="stSidebar"],
            [data-testid="stHeader"],
            [data-testid="stToolbar"],
            #MainMenu, footer,
            .stButton, .stDownloadButton, iframe {{
                display: none !important;
            }}
            .printable-invoice, .printable-invoice * {{
                visibility: visible !important;
            }}
            .printable-invoice {{
                position: fixed !important;
                left: 0 !important;
                top: 0 !important;
                width: 100% !important;
                max-width: 800px !important;
                margin: 0 auto !important;
                padding: 32px !important;
                box-shadow: none !important;
                border: 1px solid #cbd5e1 !important;
                background: #ffffff !important;
                color: #0f172a !important;
                z-index: 999999 !important;
            }}
        }}
        </style>
    """, unsafe_allow_html=True)

    # components.html() removed — caused 'undefined' text in Streamlit 1.57.
    # The collapsedControl CSS above makes the native sidebar toggle button
    # visible and styled, so no JS injection is needed.


# ─────────────────────────────────────────────────────────────
#  COMPONENT RENDER HELPERS
# ─────────────────────────────────────────────────────────────

def render_kpi(title: str, value: str, sub: str = "", icon_svg: str = "") -> str:
    t = get_theme()
    icon_html = f'<div class="kpi-icon">{icon_svg}</div>' if icon_svg else ""
    return f"""
    <div class="kpi-card">
        {icon_html}
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


def render_mcd_kpi(title: str, value: str, sub: str = "", theme: str = "gold") -> str:
    return render_kpi(title, value, sub)


def render_badge(status: str) -> str:
    if status == "System Out of Stock":
        return '<span class="badge badge-red">Out of Stock</span>'
    elif status == "System Low Stock":
        return '<span class="badge badge-yellow">Low Stock</span>'
    elif status == "Staff Reported":
        return '<span class="badge" style="background:rgba(251,146,60,.12);color:#fb923c;">Staff Reported</span>'
    else:
        return '<span class="badge badge-green">In Stock</span>'


def render_mcd_badge(status: str) -> str:
    return render_badge(status)


def render_invoice_card_html(inv: dict) -> str:
    """Renders clean HTML string for modern tax invoice card without Markdown code-block interference."""
    import icons
    main_tid = inv["items"][0]["trans_id"] if inv.get("items") else "T10001"
    logo_svg = icons.get_icon("sims_logo", 24, "#4f46e5")
    
    rows_html = []
    for item in inv.get("items", []):
        rows_html.append(
            f'<tr style="border-bottom:1px solid #f1f5f9; color:#334155;">'
            f'<td style="padding:10px 12px; font-family:\'JetBrains Mono\',monospace; font-size:0.8rem; color:#64748b;">{item["trans_id"]}</td>'
            f'<td style="padding:10px 12px; font-weight:600;">{item["product_name"]}</td>'
            f'<td style="padding:10px 12px; text-align:center;">{item["quantity"]}</td>'
            f'<td style="padding:10px 12px; text-align:right;">${item["unit_price"]:.2f}</td>'
            f'<td style="padding:10px 12px; text-align:right; font-weight:700; color:#0f172a;">${item["item_total"]:.2f}</td>'
            f'</tr>'
        )
    rows_str = "".join(rows_html)

    return (
        f'<div class="printable-invoice" style="background:#ffffff; color:#0f172a; border-radius:18px; padding:32px 36px; font-family:\'Inter\', -apple-system, sans-serif; margin-bottom:20px; border:1px solid #e2e8f0; box-shadow: 0 10px 30px rgba(0,0,0,0.06);">'
        f'<div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #6366f1; padding-bottom:18px; margin-bottom:20px;">'
        f'<div>'
        f'<div style="font-family:\'Outfit\',sans-serif; font-size:1.6rem; font-weight:900; color:#4f46e5; letter-spacing:-0.02em; display:flex; align-items:center; gap:8px;">{logo_svg} SIMS ENTERPRISE</div>'
        f'<div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Official Point of Sale Digital Tax Invoice</div>'
        f'</div>'
        f'<div style="text-align:right;">'
        f'<div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#6366f1;">Invoice Reference</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace; font-size:1.2rem; font-weight:800; color:#0f172a;">{main_tid}</div>'
        f'</div></div>'
        f'<div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:16px; background:#f8fafc; padding:14px 18px; border-radius:12px; margin-bottom:24px; border:1px solid #f1f5f9;">'
        f'<div><div style="font-size:0.72rem; color:#94a3b8; font-weight:600; text-transform:uppercase;">Date &amp; Time</div><div style="font-size:0.88rem; font-weight:600; color:#1e293b; margin-top:2px;">{inv["date"]} &nbsp; {inv["time"]}</div></div>'
        f'<div><div style="font-size:0.72rem; color:#94a3b8; font-weight:600; text-transform:uppercase;">Issued By (Cashier)</div><div style="font-size:0.88rem; font-weight:600; color:#1e293b; margin-top:2px;">{inv["sold_by"]}</div></div>'
        f'<div><div style="font-size:0.72rem; color:#94a3b8; font-weight:600; text-transform:uppercase;">Payment Status</div><div style="font-size:0.88rem; font-weight:700; color:#16a34a; margin-top:2px;">✓ PAID (CARD / CASH)</div></div></div>'
        f'<table style="width:100%; border-collapse:collapse; text-align:left; font-size:0.88rem; margin-bottom:24px;">'
        f'<thead><tr style="background:#f1f5f9; color:#475569; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;">'
        f'<th style="padding:10px 12px; border-radius:6px 0 0 6px;">Ref ID</th><th style="padding:10px 12px;">Item Name</th><th style="padding:10px 12px; text-align:center;">Qty</th><th style="padding:10px 12px; text-align:right;">Unit Price</th><th style="padding:10px 12px; text-align:right; border-radius:0 6px 6px 0;">Total</th>'
        f'</tr></thead><tbody>{rows_str}</tbody></table>'
        f'<div style="display:flex; justify-content:space-between; align-items:flex-end; border-top:2px solid #e2e8f0; padding-top:18px;">'
        f'<div style="font-size:0.75rem; color:#94a3b8; font-family:\'JetBrains Mono\',monospace;"><div>SIMS Cloud ERP Sales Engine v2.5</div><div style="letter-spacing:4px; font-size:1.1rem; color:#cbd5e1; margin-top:4px;">|||||| || |||| ||||||| |||</div></div>'
        f'<div style="text-align:right; background:linear-gradient(135deg,#4f46e5,#7c3aed); padding:16px 28px; border-radius:14px; color:#ffffff;">'
        f'<div style="font-size:0.75rem; font-weight:600; text-transform:uppercase; opacity:0.9; letter-spacing:0.06em;">Amount Paid (Grand Total)</div>'
        f'<div style="font-family:\'Outfit\',sans-serif; font-size:1.8rem; font-weight:900; line-height:1.1; margin-top:2px;">${inv["grand_total"]:.2f}</div>'
        f'</div></div></div>'
    )


def render_activity_item(timestamp: str, user_id: str, action: str) -> str:
    return f"""
    <div class="activity-item">
        <span class="ts">[{timestamp}]</span>
        <strong style="color:var(--accent); margin: 0 6px;">{user_id}</strong>
        {action}
    </div>
    """


def render_section_title(title: str, icon_svg: str = "") -> str:
    icon_part = f'<span style="opacity:.85">{icon_svg}</span>' if icon_svg else ""
    return f'<div class="section-title">{icon_part}{title}</div>'


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
    elif "cloth" in cat or "fashion" in cat:
        return "👕"
    elif "health" in cat or "pharma" in cat:
        return "💊"
    elif "sport" in cat:
        return "⚽"
    elif "book" in cat:
        return "📚"
    elif "toy" in cat or "game" in cat:
        return "🎮"
    return "📦"
