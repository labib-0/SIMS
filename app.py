"""
SIMS — Stock & Inventory Management System
app.py  |  Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import textwrap
import base64
import json
import hashlib

import db
import styles
import icons
import pdf_generator

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SIMS — Stock & Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
#  SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────
_defaults = {
    "authenticated":  False,
    "user":           None,
    "cart":           [],
    "current_page":   "Dashboard",
    "forgot_mode":    False,
    "login_attempts": 0,
    "theme":          "dark",       # "dark" | "light"
    "sidebar_open":   True,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
#  DATABASE INIT & CSS
# ─────────────────────────────────────────────────────────────
db.init_db()
styles.inject_custom_css()

# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────

def logout():
    if st.session_state.user:
        db.log_action(st.session_state.user["user_id"], "Logged out")
    for k, v in _defaults.items():
        st.session_state[k] = v


def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
    st.rerun()


def empty_plotly_chart(title: str = "", msg: str = "No data yet"):
    """Returns a Plotly figure with an empty-state annotation."""
    t = styles.get_theme()
    fig = go.Figure()
    layout = styles.get_plotly_layout(t)
    # Override xaxis/yaxis separately to avoid duplicate kwarg conflict
    layout["xaxis"] = dict(visible=False)
    layout["yaxis"] = dict(visible=False)
    fig.update_layout(
        **layout,
        title=dict(text=title, font=dict(color=t["text_muted"], size=13)),
        annotations=[dict(
            text=f"<b>{msg}</b>",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=14, color=t["text_sub"]),
        )],
        height=260,
    )
    return fig


# ─────────────────────────────────────────────────────────────
#  BARCODE & QR CODE HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def decode_barcode_or_qr_from_image(img_file):
    """
    Decodes barcodes (Code128, Code39, EAN, UPC, etc.) and QR codes from uploaded image or camera frame.
    Returns list of unique decoded text strings.
    """
    scanned_results = []
    if not img_file:
        return scanned_results

    try:
        from PIL import Image
        pil_img = Image.open(img_file)

        # 1. Try zxingcpp on PIL image directly
        try:
            import zxingcpp
            results = zxingcpp.read_barcodes(pil_img)
            for r in results:
                if r.text and r.text.strip():
                    scanned_results.append(r.text.strip())
        except Exception:
            pass

        # 2. Try converting PIL to grayscale / numpy array for zxingcpp
        if not scanned_results:
            try:
                import zxingcpp
                import numpy as np
                np_img = np.array(pil_img.convert("L"))
                results_np = zxingcpp.read_barcodes(np_img)
                for r in results_np:
                    if r.text and r.text.strip():
                        scanned_results.append(r.text.strip())
            except Exception:
                pass

        # 3. OpenCV QRCodeDetector fallback
        if not scanned_results:
            try:
                import cv2
                import numpy as np
                cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                qr_detector = cv2.QRCodeDetector()
                data, bbox, _ = qr_detector.detectAndDecode(cv_img)
                if data and data.strip():
                    scanned_results.append(data.strip())
            except Exception:
                pass

    except Exception as e:
        print(f"Barcode decode error: {e}")

    return list(set(scanned_results))


def find_product_by_code(code, products):
    """
    Finds and returns matching product dict from catalog by scanned code/payload or ID/name.
    """
    if not code:
        return None

    clean_code = str(code).strip()
    if clean_code.startswith("{") and clean_code.endswith("}"):
        try:
            data = json.loads(clean_code)
            clean_code = data.get("product_id") or data.get("id") or data.get("code") or clean_code
        except Exception:
            pass

    clean_code_lower = clean_code.lower()

    # 1. Exact match on product_id
    for p in products:
        if str(p["product_id"]).strip().lower() == clean_code_lower:
            return p

    # 2. Match on product name
    for p in products:
        if clean_code_lower == str(p["name"]).strip().lower():
            return p

    # 3. Partial match on product_id
    for p in products:
        if clean_code_lower in str(p["product_id"]).strip().lower():
            return p

    return None


def add_product_to_cart(p, qty):
    """
    Adds specified quantity of product p to st.session_state.cart.
    Returns (success: bool, msg: str)
    """
    in_cart_qty = sum(item["quantity"] for item in st.session_state.cart if item["product_id"] == p["product_id"])
    eff_avail = int(p["quantity"]) - in_cart_qty

    if eff_avail < qty:
        return False, f"Cannot add {qty}× {p['name']}. Only {eff_avail} available in stock."

    found = False
    for item in st.session_state.cart:
        if item["product_id"] == p["product_id"]:
            item["quantity"] += qty
            item["item_total"] = round(item["quantity"] * item["unit_price"], 2)
            found = True
            break

    if not found:
        st.session_state.cart.append({
            "product_id": p["product_id"],
            "name":       p["name"],
            "unit_price": float(p["price"]),
            "quantity":   qty,
            "item_total": round(qty * float(p["price"]), 2),
        })

    return True, f"Added {qty}× {p['name']} (${float(p['price']) * qty:.2f}) to cart!"


def process_scanned_code(code, products):
    """
    Matches scanned barcode/QR code (e.g. P001, EAN barcode, or JSON payload) with product catalog
    and adds it to session_state.cart.
    Returns (success: bool, message: str)
    """
    p = find_product_by_code(code, products)
    if not p:
        return False, f"Product code '{code}' not found in catalog."
    return add_product_to_cart(p, 1)


def generate_barcode_svg_base64(code_text, format_type="qrcode"):
    """
    Generates a base64 Data URI for a QR code or 1D Barcode (Code128).
    """
    try:
        import zxingcpp
        fmt = zxingcpp.BarcodeFormat.QRCode if format_type == "qrcode" else zxingcpp.BarcodeFormat.Code128
        bc = zxingcpp.create_barcode(code_text, fmt)
        svg = zxingcpp.write_barcode_to_svg(bc)
        b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{b64}"
    except Exception:
        return ""




# ─────────────────────────────────────────────────────────────
#  AUTHENTICATION — LOGIN & FORGOT PASSWORD
# ─────────────────────────────────────────────────────────────
if not st.session_state.authenticated:

    # — Theme toggle on login page —
    t_col1, t_col2 = st.columns([6, 1])
    with t_col2:
        theme_lbl = "☀️ Light" if st.session_state.theme == "dark" else "🌙 Dark"
        if st.button(theme_lbl, key="login_theme_toggle"):
            toggle_theme()

    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 1.1, 1])

    with col_center:
        if not st.session_state.forgot_mode:

            # Brand
            st.markdown(f"""
                <div style="text-align:center; margin-bottom:28px;">
                    {icons.get_icon("sims_logo", 56)}
                    <div class="login-title">SIMS Enterprise</div>
                    <div class="login-sub">Stock &amp; Inventory Management System</div>
                </div>
            """, unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                st.markdown(f"""<div style="color:{styles.get_theme()['text_muted']};font-size:.8rem;font-weight:600;
                    text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;">User ID or Email</div>""",
                    unsafe_allow_html=True)
                user_input = st.text_input("User ID or Email", placeholder="e.g. A100 or admin@sims.com",
                                           label_visibility="collapsed")
                st.markdown(f"""<div style="color:{styles.get_theme()['text_muted']};font-size:.8rem;font-weight:600;
                    text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;margin-top:12px;">Password</div>""",
                    unsafe_allow_html=True)
                password_input = st.text_input("Password", type="password", placeholder="••••••••",
                                               label_visibility="collapsed")

                st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
                login_btn = st.form_submit_button("Sign In →", type="primary", use_container_width=True)

                if login_btn:
                    user, err_msg = db.authenticate_user(user_input, password_input)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.login_attempts = 0
                        db.log_action(user["user_id"], "Logged in successfully")
                        st.toast(f"Welcome back, {user['full_name']}! 👋", icon="🎉")
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        st.error(err_msg)

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

            fa_col, dc_col = st.columns(2)
            with fa_col:
                if st.button("Forgot password?", key="btn_forgot_nav", use_container_width=True):
                    st.session_state.forgot_mode = True
                    st.rerun()
            with dc_col:
                t = styles.get_theme()
                with st.popover("Demo Credentials"):
                    st.markdown(f"""
                        <div style="font-size:.85rem;color:{t['text_muted']};line-height:2;">
                            {icons.get_icon('users',14,t['accent'])} &nbsp;<b>Admin</b>: <code>A100</code> / <code>Admin123</code><br>
                            {icons.get_icon('users',14,t['accent'])} &nbsp;<b>Manager</b>: <code>M100</code> / <code>Asad123</code><br>
                            {icons.get_icon('users',14,t['accent'])} &nbsp;<b>Staff</b>: <code>S100</code> / <code>Masuk123</code>
                        </div>
                    """, unsafe_allow_html=True)

        else:
            # Forgot Password
            st.markdown(f"""
                <div style="text-align:center;margin-bottom:24px;">
                    {icons.get_icon("audit",48,styles.get_theme()['accent'])}
                    <div class="login-title" style="font-size:1.6rem;">Reset Password</div>
                    <div class="login-sub">Enter your details to verify identity</div>
                </div>
            """, unsafe_allow_html=True)

            with st.form("forgot_form"):
                f_uid   = st.text_input("User ID", placeholder="e.g. A100")
                f_name  = st.text_input("Full Name", placeholder="e.g. Default Admin")
                f_dob   = st.text_input("Date of Birth", placeholder="DD/MM/YYYY")
                f_email = st.text_input("Email Address", placeholder="admin@sims.com")
                f_new_pass = st.text_input("New Password", type="password", help="Min 6 chars (Upper, Lower, Digit)")
                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                reset_btn = st.form_submit_button("Reset Password", type="primary", use_container_width=True)

                if reset_btn:
                    success, msg = db.reset_password_forgot(f_uid, f_name, f_dob, f_email, f_new_pass)
                    if success:
                        st.success(msg)
                        st.session_state.forgot_mode = False
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if st.button("← Back to Sign In", use_container_width=True):
                st.session_state.forgot_mode = False
                st.rerun()

    st.stop()


# ─────────────────────────────────────────────────────────────
#  MAIN APP — AUTHENTICATED
# ─────────────────────────────────────────────────────────────
current_user = st.session_state.user
role         = current_user["role"]
user_id      = current_user["user_id"]
full_name    = current_user["full_name"]
db_info      = db.get_db_info()
t            = styles.get_theme()
is_light     = st.session_state.theme == "light"


# ─────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo / Brand
    logo_col, name_col = st.columns([1, 2.2])
    with logo_col:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=52)
        else:
            st.markdown(icons.get_icon("sims_logo", 48), unsafe_allow_html=True)
    with name_col:
        st.markdown(f"""
            <div style="margin-top:6px;">
                <div style="font-family:var(--font-heading);font-weight:800;font-size:1.1rem;
                    color:{t['text_heading']};">SIMS</div>
                <div style="font-size:0.72rem;color:{t['text_muted']};">Enterprise v2.0</div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # User Info Card
    db_badge_color = t["success"] if db_info["is_xampp"] else "#fb923c"
    db_badge_label = "🟢 MySQL" if db_info["is_xampp"] else "📁 SQLite"

    st.markdown(f"""
        <div class="sidebar-user-card">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <div style="width:38px;height:38px;border-radius:10px;
                    background:linear-gradient(135deg,{t['accent2']},{t['accent3']});
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.1rem;font-weight:700;color:#fff;">
                    {full_name[0].upper()}
                </div>
                <div>
                    <div style="font-weight:700;font-size:.95rem;color:{t['text_heading']};">{full_name}</div>
                    <div style="font-size:.75rem;color:{t['text_muted']};">ID: <code>{user_id}</code></div>
                </div>
            </div>
            <div style="display:flex;gap:6px;flex-wrap:wrap;">
                <span class="badge badge-indigo">{role}</span>
                <span style="background:rgba(74,222,128,.1);color:{db_badge_color};
                    display:inline-flex;align-items:center;padding:3px 10px;
                    border-radius:99px;font-size:.72rem;font-weight:600;">{db_badge_label}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown(f"""
        <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;
            letter-spacing:.1em;color:{t['text_sub']};margin-bottom:8px;">Navigation</div>
    """, unsafe_allow_html=True)

    if role == "Admin":
        nav_options = ["Dashboard", "POS Terminal", "Product Catalog", "Stock Operations",
                       "User Management", "Transactions", "Reports", "Audit Logs", "Backup & Restore", "My Profile"]
    elif role == "Store Manager":
        nav_options = ["Dashboard", "Product Catalog", "Restock Requests",
                       "Transactions", "Reports", "My Profile"]
    else:
        nav_options = ["Dashboard", "POS Terminal", "Product Catalog",
                       "Restock Requests", "Transactions", "My Profile"]

    for opt in nav_options:
        icon_html = icons.get_nav_icon(opt, size=15,
            color=t["accent"] if st.session_state.current_page == opt else t["text_muted"])
        is_active = st.session_state.current_page == opt
        btn_type  = "primary" if is_active else "secondary"
        if st.button(f"{opt}", key=f"nav_{opt}", use_container_width=True, type=btn_type):
            st.session_state.current_page = opt
            st.rerun()

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    st.divider()

    if st.button("🚪 Sign Out", key="sign_out_btn", use_container_width=True):
        logout()
        st.rerun()


# ─────────────────────────────────────────────────────────────
#  TOP HEADER BAR
# ─────────────────────────────────────────────────────────────
page = st.session_state.current_page

# Low stock alert count for notification badge
try:
    all_products_for_notif = db.get_all_products()
    alert_count = sum(1 for p in all_products_for_notif
                      if p["stock_alert"] in ["System Low Stock", "System Out of Stock", "Staff Reported"])
except Exception:
    alert_count = 0

notif_html = (f'<span class="notif-badge">{alert_count}</span>' if alert_count > 0 else "")
bell_svg   = icons.get_icon("bell", 18, t["danger"] if alert_count > 0 else t["text_muted"])
db_eng_color = t["success"] if db_info["is_xampp"] else "#fb923c"
db_svg     = icons.get_icon("database", 14, db_eng_color)
activity_svg = icons.get_icon("activity", 14, t["accent"])
# (emoji used directly in button label — no SVG needed here)

hdr_col1, hdr_col2 = st.columns([3, 1])
with hdr_col1:
    st.markdown(f"""
        <div class="sims-top-header" style="margin-bottom:20px;">
            <div>
                <h1>SIMS Control Center</h1>
                <div style="color:{t['text_muted']};font-size:.85rem;margin-top:4px;display:flex;align-items:center;gap:12px;">
                    <span>{activity_svg} &nbsp;{full_name} &bull; <span style="color:{t['badge_role_text']}">{role}</span></span>
                    <span>{db_svg} &nbsp;<span style="color:{db_eng_color}">{db_info['engine']}</span></span>
                    <span style="color:{t['text_sub']}">{datetime.now().strftime('%d %b %Y  %H:%M')}</span>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:16px;">
                <div style="font-size:1.1rem;cursor:default;">{bell_svg}{notif_html}</div>
                <div style="font-family:var(--font-mono);font-size:.8rem;color:{t['text_sub']};">
                    {page}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with hdr_col2:
    th_label = "☀️ Light Mode" if not is_light else "🌙 Dark Mode"
    if st.button(th_label, key="header_theme_toggle", use_container_width=True):
        toggle_theme()


# ═══════════════════════════════════════════════════════════════
#  QUERY PARAMETER BARCODE SCAN LISTENER
# ═══════════════════════════════════════════════════════════════
query_scan = st.query_params.get("scan") or st.query_params.get("barcode") or st.query_params.get("qr")
if query_scan and st.session_state.get("authenticated"):
    products_all = db.get_all_products()
    matched_p = find_product_by_code(query_scan, products_all)
    if matched_p:
        st.session_state["pending_scan_product"] = matched_p
        st.session_state["current_page"] = "POS Terminal"
    else:
        st.session_state["scan_error"] = f"❌ Scanned code '{query_scan}' not found in catalog."
        st.session_state["current_page"] = "POS Terminal"
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()



# ═══════════════════════════════════════════════════════════════
#  PAGE ROUTING
# ═══════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────────
#  1. DASHBOARD
# ──────────────────────────────────────────────────────────────
if page == "Dashboard":
    products     = db.get_all_products()
    transactions = db.get_all_transactions()
    users        = db.get_all_users()
    logs         = db.get_audit_logs()

    total_revenue   = sum(float(tx["total_price"]) for tx in transactions)
    low_stock_count = sum(1 for p in products if p["stock_alert"] in
                          ["System Low Stock", "System Out of Stock", "Staff Reported"])
    total_products  = len(products)
    total_items     = sum(int(p["quantity"]) for p in products)
    total_valuation = sum(float(p["price"]) * int(p["quantity"]) for p in products)

    # — KPI CARDS —
    kpi_data = [
        ("Total Revenue",     f"${total_revenue:,.2f}",  f"{len(transactions)} Transactions", "currency",       t["accent"]),
        ("Stock Alerts",      f"{low_stock_count}",       "Requires Attention",                "alert_triangle", t["danger"]),
        ("Total Products",    f"{total_products}",        f"{total_items:,} Items in Stock",   "products",       t["accent3"]),
        ("Inventory Value",   f"${total_valuation:,.2f}", "Total Stock Valuation",             "box",            t["info"]),
        ("Active Users",      f"{len(users)}",            "System Accounts",                   "users",          t["success"]),
    ]

    kpi_cols = st.columns(5)
    for col, (title, value, sub, icon_name, color) in zip(kpi_cols, kpi_data):
        with col:
            icon_svg = icons.get_icon(icon_name, 20, color)
            st.markdown(styles.render_kpi(title, value, sub, icon_svg), unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # — CHARTS ROW 1 —
    chart_col1, chart_col2 = st.columns([1.2, 1])

    PALETTE_DARK  = ["#818cf8","#a78bfa","#60a5fa","#34d399","#fbbf24","#f87171","#fb923c","#e879f9"]
    PALETTE_LIGHT = ["#6366f1","#7c3aed","#2563eb","#059669","#d97706","#dc2626","#ea580c","#9333ea"]
    palette = PALETTE_LIGHT if is_light else PALETTE_DARK

    with chart_col1:
        with st.container(border=True):
            st.markdown(styles.render_section_title("Inventory by Category",
                icons.get_icon("products", 17, t["accent"])), unsafe_allow_html=True)

            df_prod = pd.DataFrame(products)
            if not df_prod.empty:
                cat_df = df_prod.groupby("category")["quantity"].sum().reset_index()
                fig_pie = px.pie(
                    cat_df, values="quantity", names="category", hole=0.5,
                    color_discrete_sequence=palette,
                )
                fig_pie.update_traces(
                    textposition="outside",
                    textinfo="label+percent",
                    hovertemplate="<b>%{label}</b><br>%{value} units<br>%{percent}<extra></extra>",
                )
                fig_pie.update_layout(
                    **styles.get_plotly_layout(t),
                    height=300,
                    showlegend=True,
                )
                fig_pie.update_layout(legend=dict(orientation="v", x=1.02, y=0.5))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.plotly_chart(empty_plotly_chart("Inventory by Category",
                    "Add products to see distribution"), use_container_width=True)

    with chart_col2:
        with st.container(border=True):
            st.markdown(styles.render_section_title("Top Revenue Products",
                icons.get_icon("reports", 17, t["accent"])), unsafe_allow_html=True)

            df_tx = pd.DataFrame(transactions)
            if not df_tx.empty and "product_name" in df_tx.columns:
                top_df = (df_tx.groupby("product_name")["total_price"]
                          .sum().reset_index()
                          .sort_values("total_price", ascending=True)
                          .tail(6))
                fig_bar = go.Figure(go.Bar(
                    x=top_df["total_price"],
                    y=top_df["product_name"],
                    orientation="h",
                    marker=dict(
                        color=top_df["total_price"],
                        colorscale=[[0, palette[1]], [1, palette[0]]],
                        showscale=False,
                        line=dict(width=0),
                    ),
                    hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>",
                    text=[f"${v:,.0f}" for v in top_df["total_price"]],
                    textposition="outside",
                    textfont=dict(color=t["text_muted"], size=11),
                ))
                fig_bar.update_layout(
                    **styles.get_plotly_layout(t),
                    height=300,
                    xaxis_title="Revenue ($)",
                    yaxis_title=None,
                    bargap=0.3,
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.plotly_chart(empty_plotly_chart("Top Revenue Products",
                    "No sales recorded yet"), use_container_width=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # — CHARTS ROW 2 —
    chart_col3, chart_col4 = st.columns([1, 1])

    with chart_col3:
        with st.container(border=True):
            st.markdown(styles.render_section_title("Stock Level Overview",
                icons.get_icon("stock", 17, t["accent"])), unsafe_allow_html=True)

            if products:
                df_stock = pd.DataFrame(products)[["name","quantity","min_stock"]].head(10)
                fig_stock = go.Figure()
                fig_stock.add_trace(go.Bar(
                    name="Current Stock", x=df_stock["name"], y=df_stock["quantity"],
                    marker_color=palette[0],
                    hovertemplate="<b>%{x}</b><br>Stock: %{y}<extra></extra>",
                ))
                fig_stock.add_trace(go.Bar(
                    name="Min Level", x=df_stock["name"], y=df_stock["min_stock"],
                    marker_color=palette[5],
                    hovertemplate="<b>%{x}</b><br>Min: %{y}<extra></extra>",
                ))
                fig_stock.update_layout(
                    **styles.get_plotly_layout(t),
                    height=290, barmode="overlay", bargap=0.25,
                    xaxis_tickangle=-30,
                )
            else:
                st.plotly_chart(empty_plotly_chart("Stock Level Overview",
                    "No products added yet"), use_container_width=True)

    with chart_col4:
        with st.container(border=True):
            st.markdown(styles.render_section_title("Sales by Category",
                icons.get_icon("currency", 17, t["accent"])), unsafe_allow_html=True)

            df_tx2 = pd.DataFrame(transactions) if transactions else pd.DataFrame()
            df_prod2 = pd.DataFrame(products) if products else pd.DataFrame()

            if not df_tx2.empty and not df_prod2.empty and "product_id" in df_tx2.columns:
                merged = df_tx2.merge(df_prod2[["product_id","category"]], on="product_id", how="left")
                cat_sales = merged.groupby("category")["total_price"].sum().reset_index()
                fig_cat = px.bar(
                    cat_sales.sort_values("total_price", ascending=False),
                    x="category", y="total_price",
                    color="category",
                    color_discrete_sequence=palette,
                    labels={"category": "Category", "total_price": "Revenue ($)"},
                )
                fig_cat.update_layout(
                    **styles.get_plotly_layout(t),
                    height=290,
                    showlegend=False,
                    xaxis_tickangle=-20,
                )
                fig_cat.update_traces(
                    hovertemplate="<b>%{x}</b><br>$%{y:,.2f}<extra></extra>",
                )
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.plotly_chart(empty_plotly_chart("Sales by Category",
                    "No sales data available yet"), use_container_width=True)

    # — ACTIVITY FEED —
    st.markdown(styles.render_section_title("Recent System Activity",
        icons.get_icon("activity", 17, t["accent"])), unsafe_allow_html=True)

    if logs:
        for l in logs[:8]:
            st.markdown(styles.render_activity_item(
                l["timestamp"], l["user_id"], l["action"]
            ), unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="activity-item" style="text-align:center;color:{t['text_sub']};border-left:3px solid {t['card_border']};">
                No activity recorded yet.
            </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
#  2. POS TERMINAL
# ──────────────────────────────────────────────────────────────
elif page == "POS Terminal":
    st.markdown(styles.render_section_title("POS Terminal & Checkout",
        icons.get_icon("pos", 20, t["accent"])), unsafe_allow_html=True)

    if "scan_toast" in st.session_state and st.session_state.scan_toast:
        st.toast(st.session_state.scan_toast, icon="🛒")
        st.session_state.scan_toast = None

    if "scan_error" in st.session_state and st.session_state.scan_error:
        st.error(st.session_state.scan_error)
        st.session_state.scan_error = None

    products = db.get_all_products()

    # ─────────────────────────────────────────────────────────────
    #  INTERACTIVE SCANNED PRODUCT CONFIRMATION CARD
    # ─────────────────────────────────────────────────────────────
    if st.session_state.get("pending_scan_product"):
        p_scanned = st.session_state["pending_scan_product"]
        in_cart_qty = sum(item["quantity"] for item in st.session_state.cart if item["product_id"] == p_scanned["product_id"])
        eff_avail = int(p_scanned["quantity"]) - in_cart_qty

        st.markdown(f"""
            <div style="background:linear-gradient(135deg, {t['accent2']}25, {t['accent3']}25);
                border:2px solid {t['accent']};border-radius:16px;padding:20px;margin-bottom:20px;
                box-shadow:0 10px 30px rgba(99,102,241,0.25);">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
                    <div style="display:flex;align-items:center;gap:14px;">
                        <div style="font-size:2rem;background:{t['accent_glow']};width:52px;height:52px;
                            border-radius:14px;display:flex;align-items:center;justify-content:center;">
                            🛒
                        </div>
                        <div>
                            <div style="font-size:1.15rem;font-weight:800;color:{t['text_heading']};">
                                {p_scanned['name']} <span style="font-size:.85rem;color:{t['accent']};">({p_scanned['product_id']})</span>
                            </div>
                            <div style="font-size:.85rem;color:{t['text_muted']};margin-top:2px;">
                                Category: {p_scanned['category']} &bull; Price: <strong style="color:{t['text_heading']};">${float(p_scanned['price']):.2f}</strong> &bull; Available Stock: <strong>{eff_avail}</strong>
                            </div>
                        </div>
                    </div>
                    <div style="font-size:1.4rem;font-weight:900;color:{t['success']};">
                        ${float(p_scanned['price']):.2f} / unit
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if eff_avail > 0:
            c_confirm1, c_confirm2, c_confirm3 = st.columns([1.5, 2, 1.2])
            with c_confirm1:
                add_qty = st.number_input("Quantity to Add", min_value=1, max_value=eff_avail, value=1, key="confirm_scanned_qty_input")
            with c_confirm2:
                st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                if st.button(f"🛒 Add {add_qty}× to Cart (${float(p_scanned['price']) * add_qty:.2f})", type="primary", use_container_width=True, key="btn_add_scanned_cart"):
                    success, msg = add_product_to_cart(p_scanned, add_qty)
                    if success:
                        st.toast(msg, icon="🛒")
                        st.session_state["pending_scan_product"] = None
                        st.rerun()
                    else:
                        st.error(msg)
            with c_confirm3:
                st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                if st.button("✕ Cancel & Rescan", use_container_width=True, key="btn_cancel_scanned"):
                    st.session_state["pending_scan_product"] = None
                    st.rerun()
        else:
            st.error(f"⚠️ '{p_scanned['name']}' is currently out of stock ({eff_avail} available).")
            if st.button("✕ Dismiss & Rescan", key="btn_dismiss_out_of_stock"):
                st.session_state["pending_scan_product"] = None
                st.rerun()

    col_left, col_right = st.columns([1.6, 1])

    with col_left:
        # ─────────────────────────────────────────────────────────────
        #  POS SCANNER (LIVE CAMERA & PRINTABLE CODES ONLY)
        # ─────────────────────────────────────────────────────────────
        with st.expander("📱 **Live Camera & Barcode Scanner**", expanded=True):
            scan_tab1, scan_tab2 = st.tabs([
                "⚡ Live HTML5 Camera Scanner",
                "🏷️ Printable Barcodes & QR Codes"
            ])

            with scan_tab1:
                if st.session_state.get("pending_scan_product"):
                    st.info("⏸️ **Camera paused while product confirmation is active above.** Select quantity & tap **Add to Cart** or **Cancel & Rescan** above to resume live camera scanning.")
                else:
                    st.markdown(f"""
                        <div style="font-size:.85rem;color:{t['text_muted']};margin-bottom:10px;">
                            Point your mobile camera at a barcode or QR code. It will detect the item and prompt you to choose quantity!
                        </div>
                    """, unsafe_allow_html=True)
                    html5_code = """
                    <div style="background:#0b0f19; padding:16px; border-radius:12px; text-align:center; color:#f8fafc; font-family:sans-serif; border:1px solid #1e293b;">
                        <div id="qr-reader" style="width:100%; max-width:400px; margin:0 auto; border-radius:8px; overflow:hidden;"></div>
                        <div id="qr-reader-results" style="margin-top:12px; font-weight:600; font-size:14px; color:#38bdf8;">🎥 Camera Active — Align Barcode or QR Code</div>
                    </div>

                    <script src="https://unpkg.com/html5-qrcode"></script>
                    <script>
                        let isProcessingScan = false;
                        function onScanSuccess(decodedText, decodedResult) {
                            if (isProcessingScan) return;
                            isProcessingScan = true;
                            
                            const resElem = document.getElementById('qr-reader-results');
                            if (resElem) {
                                resElem.innerText = '✅ Code Detected: ' + decodedText + ' — Opening confirmation...';
                            }
                            
                            try {
                                if (typeof html5QrcodeScanner !== 'undefined' && html5QrcodeScanner) {
                                    html5QrcodeScanner.clear();
                                }
                            } catch(e) {}
                            
                            setTimeout(function() {
                                try {
                                    if (window.top) {
                                        const currentUrl = new URL(window.top.location.href);
                                        currentUrl.searchParams.set('scan', decodedText);
                                        window.top.location.href = currentUrl.toString();
                                    }
                                } catch(e) {
                                    console.log('Redirecting fallback...', e);
                                }
                            }, 150);
                        }

                        let html5QrcodeScanner = new Html5QrcodeScanner(
                            "qr-reader",
                            { fps: 10, qrbox: { width: 250, height: 250 }, rememberLastUsedCamera: true },
                            /* verbose= */ false
                        );
                        html5QrcodeScanner.render(onScanSuccess);
                    </script>
                    """
                    st.components.v1.html(html5_code, height=440, scrolling=False)

            with scan_tab2:
                btn_col1, btn_col2 = st.columns([2.5, 1])
                with btn_col1:
                    st.markdown(f"""
                        <div style="font-size:.85rem;color:{t['text_muted']};margin-bottom:8px;">
                            <strong>Product Barcodes & QR Codes Catalog:</strong> Scan these codes on screen or generate a PDF printable sheet for all products!
                        </div>
                    """, unsafe_allow_html=True)
                with btn_col2:
                    pdf_bytes, pdf_file_path = pdf_generator.generate_barcode_catalog_pdf(products)
                    st.download_button(
                        label="🖨️ Print Now (PDF)",
                        data=pdf_bytes,
                        file_name="SIMS_Product_Barcodes_Catalog.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                        key="btn_download_barcode_catalog"
                    )

                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                cols_b = st.columns(3)
                for idx, p in enumerate(products):
                    c_idx = idx % 3
                    with cols_b[c_idx]:
                        qr_uri = generate_barcode_svg_base64(p["product_id"], "qrcode")
                        bc_uri = generate_barcode_svg_base64(p["product_id"], "code128")
                        st.markdown(f"""
                            <div style="background:{t['input_bg']};border:1px solid {t['card_border']};border-radius:12px;padding:12px;text-align:center;margin-bottom:12px;">
                                <div style="font-weight:700;font-size:.9rem;color:{t['text_heading']};">{p['name']}</div>
                                <div style="font-size:.75rem;color:{t['accent']};">{p['product_id']} — ${float(p['price']):.2f}</div>
                                <div style="display:flex;justify-content:center;gap:6px;margin-top:8px;background:#ffffff;padding:8px;border-radius:8px;">
                                    <img src="{qr_uri}" style="width:64px;height:64px;" title="QR Code: {p['product_id']}"/>
                                    <img src="{bc_uri}" style="width:90px;height:64px;object-fit:contain;" title="Barcode: {p['product_id']}"/>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="section-title" style="font-size:.95rem;margin-top:16px;">
                {icons.get_icon("products",15,t["text_muted"])} &nbsp; Product Catalog
            </div>
        """, unsafe_allow_html=True)

        search_kw = st.text_input("Search catalog",
                                  placeholder="Search Product Name, ID, or Category...",
                                  label_visibility="collapsed")

        filtered_p = [
            p for p in products
            if search_kw.lower() in p["product_id"].lower()
            or search_kw.lower() in p["name"].lower()
            or search_kw.lower() in p["category"].lower()
        ]

        for p in filtered_p:
            in_cart_qty = sum(item["quantity"] for item in st.session_state.cart
                              if item["product_id"] == p["product_id"])
            eff_avail = int(p["quantity"]) - in_cart_qty
            cat_icon  = styles.get_category_icon(p["category"])
            stock_badge = (
                f'<span class="badge badge-red">Out of Stock</span>'
                if eff_avail <= 0 else (
                f'<span class="badge badge-yellow">Low Stock</span>'
                if p["stock_alert"] == "System Low Stock" else
                f'<span class="badge badge-green">In Stock</span>'
            ))

            st.markdown(f"""
                <div class="kiosk-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div style="display:flex;align-items:center;gap:14px;">
                            <div style="font-size:1.7rem;background:{t['accent_glow']};
                                width:46px;height:46px;border-radius:12px;
                                display:flex;align-items:center;justify-content:center;">
                                {cat_icon}
                            </div>
                            <div>
                                <div style="font-weight:700;font-size:1rem;color:{t['text_heading']};">
                                    {p['name']}
                                    <span style="font-size:.75rem;color:{t['text_sub']};"> ({p['product_id']})</span>
                                </div>
                                <div style="font-size:.78rem;color:{t['accent']};margin-top:2px;">{p['category']}</div>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-weight:800;font-size:1.15rem;color:{t['text_heading']};">
                                ${float(p['price']):.2f}
                            </div>
                            <div style="font-size:.75rem;color:{t['text_muted']};margin-top:2px;">
                                Stock: <strong>{eff_avail}</strong> &nbsp; {stock_badge}
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            c_act1, c_act2 = st.columns([2, 1])
            with c_act1:
                if eff_avail > 0:
                    add_qty = st.number_input("Qty", min_value=1, max_value=eff_avail, value=1,
                                              key=f"qty_{p['product_id']}", label_visibility="collapsed")
                else:
                    st.caption("Unavailable")
            with c_act2:
                if eff_avail > 0:
                    if st.button("Add +", key=f"add_{p['product_id']}", type="primary", use_container_width=True):
                        found = False
                        for item in st.session_state.cart:
                            if item["product_id"] == p["product_id"]:
                                item["quantity"]   += add_qty
                                item["item_total"]  = round(item["quantity"] * item["unit_price"], 2)
                                found = True
                                break
                        if not found:
                            st.session_state.cart.append({
                                "product_id": p["product_id"],
                                "name":       p["name"],
                                "unit_price": float(p["price"]),
                                "quantity":   add_qty,
                                "item_total": round(add_qty * float(p["price"]), 2),
                            })
                        st.toast(f"Added {add_qty}× {p['name']}", icon="🛒")
                        st.rerun()

    with col_right:
        cart_count = sum(i["quantity"] for i in st.session_state.cart)
        st.markdown(f"""
            <div class="section-title" style="font-size:.95rem;">
                {icons.get_icon("pos",15,t["text_muted"])} &nbsp; Shopping Cart
                {f'<span class="notif-badge">{cart_count}</span>' if cart_count else ""}
            </div>
        """, unsafe_allow_html=True)

        if not st.session_state.cart:
            st.markdown(f"""
                <div class="sims-card" style="text-align:center;padding:36px 20px;">
                    {icons.get_icon("pos", 40, t['text_sub'])}
                    <div style="color:{t['text_sub']};margin-top:12px;font-size:.9rem;">
                        Cart is empty.<br>Add items from the catalog.
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            cart_total = sum(item["item_total"] for item in st.session_state.cart)

            for idx, item in enumerate(st.session_state.cart):
                cc1, cc2, cc3 = st.columns([3, 1.5, 0.8])
                cc1.markdown(
                    f"**{item['name']}**<br>"
                    f"<small style='color:{t['text_muted']};'>${item['unit_price']:.2f} × {item['quantity']}</small>",
                    unsafe_allow_html=True,
                )
                cc2.markdown(f"<strong style='color:{t['text_heading']};'>${item['item_total']:.2f}</strong>",
                             unsafe_allow_html=True)
                if cc3.button("✕", key=f"del_cart_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                st.divider()

            # Total panel
            st.markdown(f"""
                <div style="background:linear-gradient(135deg,{t['accent2']}22,{t['accent3']}11);
                    border:1px solid {t['card_border']};border-radius:16px;padding:20px;
                    text-align:center;margin:16px 0;">
                    <div style="font-size:.78rem;color:{t['text_muted']};text-transform:uppercase;
                        letter-spacing:.08em;">Grand Total</div>
                    <div style="font-family:var(--font-heading);font-size:2rem;font-weight:900;
                        color:{t['text_heading']};margin-top:4px;">${cart_total:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("🗑 Clear Cart", use_container_width=True):
                st.session_state.cart = []
                st.rerun()

            if c_btn2.button("Checkout →", type="primary", use_container_width=True):
                success, msg, invoice = db.process_pos_checkout(st.session_state.cart, user_id)
                if success:
                    pdf_bytes, pdf_path = pdf_generator.generate_invoice_pdf(invoice)
                    st.session_state.last_invoice   = invoice
                    st.session_state.last_pdf_bytes  = pdf_bytes
                    st.session_state.last_pdf_path   = pdf_path
                    st.session_state.cart = []
                    st.toast(f"✅ Invoice saved to: {pdf_path}", icon="💾")
                    st.rerun()
                else:
                    st.error(msg)

        # Invoice preview
        if "last_invoice" in st.session_state and st.session_state.last_invoice:
            inv = st.session_state.last_invoice
            first_item = inv["items"][0] if inv.get("items") else {"trans_id": "T10001"}
            main_tid   = first_item.get("trans_id", "T10001")

            st.divider()
            st.markdown(f"""
                <div class="section-title">
                    {icons.get_icon("transactions",18,t["accent"])} Tax Invoice &amp; Receipt ({main_tid})
                </div>
            """, unsafe_allow_html=True)

            st.html(styles.render_invoice_card_html(inv))

            ic1, ic2 = st.columns([2, 1])
            with ic1:
                st.components.v1.html(
                    """<button onclick="window.parent.print()"
                        style="background:linear-gradient(135deg,#4f46e5,#7c3aed); color:#ffffff;
                        font-family:'Inter',sans-serif; font-weight:700; border:none; padding:12px 24px;
                        border-radius:12px; cursor:pointer; width:100%; height:46px; font-size:15px;
                        box-shadow:0 4px 14px rgba(79,70,229,0.3); transition:all 0.2s ease;">
                        🖨️ Print Receipt
                    </button>""",
                    height=56,
                )
            with ic2:
                if st.button("✕ Close", key="btn_close_inv", use_container_width=True):
                    del st.session_state.last_invoice
                    if "last_pdf_bytes" in st.session_state:
                        del st.session_state.last_pdf_bytes
                    st.rerun()


# ──────────────────────────────────────────────────────────────
#  3. PRODUCT CATALOG
# ──────────────────────────────────────────────────────────────
elif page in ["Product Catalog", "Product Management"]:
    st.markdown(styles.render_section_title("Product Catalog",
        icons.get_icon("products", 20, t["accent"])), unsafe_allow_html=True)

    products = db.get_all_products()

    # Filters
    fc1, fc2 = st.columns([2, 1.5])
    with fc1:
        search_query = st.text_input("Search catalog", placeholder="Search ID, Name, Category...",
                                     label_visibility="collapsed")
    with fc2:
        status_filter = st.selectbox("Filter by Status",
            ["All Statuses", "System Low Stock", "System Out of Stock", "Staff Reported", "In Stock"])

    filtered = products
    if search_query:
        q = search_query.lower()
        filtered = [p for p in filtered
                    if q in p["product_id"].lower() or q in p["name"].lower() or q in p["category"].lower()]
    if status_filter != "All Statuses":
        if status_filter == "In Stock":
            filtered = [p for p in filtered if p["stock_alert"] == "-"]
        else:
            filtered = [p for p in filtered if p["stock_alert"] == status_filter]

    if "flash_product_msg" in st.session_state and st.session_state.flash_product_msg:
        st.success(st.session_state.flash_product_msg)
        del st.session_state.flash_product_msg

    # Add product form
    if role in ["Admin", "Store Manager"]:
        with st.expander(f"➕  Add New Product"):
            with st.form("add_product_form"):
                ap1, ap2 = st.columns(2)
                p_name  = ap1.text_input("Product Name")
                p_cat   = ap2.text_input("Category")
                p_price = ap1.number_input("Unit Price ($)", min_value=0.0, step=0.5)
                p_qty   = ap2.number_input("Initial Quantity", min_value=0, step=1)
                p_min   = ap1.number_input("Minimum Stock Level", min_value=0, step=1)
                add_submit = st.form_submit_button("Save Product", type="primary")
                if add_submit:
                    succ, msg = db.add_product(p_name, p_cat, p_price, p_qty, p_min, user_id)
                    if succ:
                        st.toast(f"Product '{p_name}' saved! ID: {msg}", icon="🎉")
                        st.session_state.flash_product_msg = (
                            f"🎉 Product '{p_name}' (ID: **{msg}**) saved successfully!")
                        st.rerun()
                    else:
                        st.error(msg)

    # Table
    st.markdown(f"<div style='color:{t['text_muted']};font-size:.85rem;margin-bottom:8px;'>"
                f"Showing <strong>{len(filtered)}</strong> products</div>", unsafe_allow_html=True)

    if filtered:
        display_rows = [{
            "ID":         p["product_id"],
            "Item Name":  p["name"],
            "Category":   p["category"],
            "Price ($)":  f"${float(p['price']):.2f}",
            "Stock Qty":  p["quantity"],
            "Min Level":  p["min_stock"],
            "Restock Req":p["restock_qty"],
            "Status":     p["stock_alert"],
        } for p in filtered]
        st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No products match your filter.")

    # Actions
    if role in ["Admin", "Store Manager"]:
        st.divider()
        st.markdown(styles.render_section_title("Product Actions",
            icons.get_icon("stock", 16, t["accent"])), unsafe_allow_html=True)

        act_col1, act_col2 = st.columns(2)

        with act_col1:
            st.markdown(f"<div style='font-weight:600;color:{t['text_heading']};margin-bottom:8px;'>Edit Product</div>",
                        unsafe_allow_html=True)
            if products:
                sel_pid = st.selectbox("Select Product to Edit",
                    [p["product_id"] for p in products], key="edit_pid_select")
                target_p = next((p for p in products if p["product_id"] == sel_pid), None)
                if target_p:
                    with st.form("edit_prod_form"):
                        e_name  = st.text_input("Name",       value=target_p["name"])
                        e_cat   = st.text_input("Category",   value=target_p["category"])
                        e_price = st.number_input("Price ($)", value=float(target_p["price"]), min_value=0.0)
                        e_min   = st.number_input("Min Stock", value=int(target_p["min_stock"]), min_value=0)
                        if st.form_submit_button("Update Product", type="primary"):
                            s, msg = db.update_product(sel_pid, e_name, e_cat, e_price, e_min, user_id)
                            st.success(msg) if s else st.error(msg)
                            if s:
                                st.rerun()

        with act_col2:
            if role == "Admin" and products:
                st.markdown(f"<div style='font-weight:600;color:{t['text_heading']};margin-bottom:8px;'>Delete Product</div>",
                            unsafe_allow_html=True)
                del_pid = st.selectbox("Select Product to Delete",
                    ["Select..."] + [p["product_id"] for p in products], key="del_pid_select")
                if del_pid != "Select...":
                    if st.button(f"Confirm Delete  {del_pid}", type="primary"):
                        s, msg = db.delete_product(del_pid, user_id)
                        st.success(msg) if s else st.error(msg)
                        if s:
                            st.rerun()


# ──────────────────────────────────────────────────────────────
#  4. STOCK OPERATIONS / RESTOCK REQUESTS
# ──────────────────────────────────────────────────────────────
elif page in ["Stock Operations", "Restock Requests"]:
    st.markdown(styles.render_section_title("Stock Operations & Replenishment",
        icons.get_icon("stock", 20, t["accent"])), unsafe_allow_html=True)

    products = db.get_all_products()

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown(f"""
            <div class="sims-card">
                <div class="section-title" style="margin-bottom:16px;">
                    {icons.get_icon("box",16,t["success"])} Add Stock Now
                </div>
        """, unsafe_allow_html=True)
        if products:
            r_pid_str = st.selectbox("Select Product to Restock",
                [p["product_id"] + " — " + p["name"] for p in products], key="restock_sel")
            if r_pid_str:
                pid = r_pid_str.split(" — ")[0]
                target_p = next((p for p in products if p["product_id"] == pid), None)
                if target_p:
                    st.info(
                        f"Current Stock: **{target_p['quantity']}** | "
                        f"Status: `{target_p['stock_alert']}` | "
                        f"Pending: **{target_p['restock_qty']}**"
                    )
                    with st.form("restock_form"):
                        add_units = st.number_input("Units to Add", min_value=1, value=20)
                        if st.form_submit_button("Add Stock →", type="primary", use_container_width=True):
                            s, msg = db.restock_product(pid, add_units, user_id)
                            st.success(msg) if s else st.error(msg)
                            if s:
                                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r2:
        st.markdown(f"""
            <div class="sims-card">
                <div class="section-title" style="margin-bottom:16px;">
                    {icons.get_icon("bell",16,t["warning"])} Request Restock
                </div>
        """, unsafe_allow_html=True)
        if products:
            req_pid_str = st.selectbox("Select Product",
                [p["product_id"] + " — " + p["name"] for p in products], key="req_sel")
            if req_pid_str:
                req_pid = req_pid_str.split(" — ")[0]
                with st.form("request_form"):
                    req_units = st.number_input("Quantity to Request", min_value=1, value=25)
                    if st.form_submit_button("Submit Request →", type="primary", use_container_width=True):
                        s, msg = db.request_restock(req_pid, req_units, user_id)
                        st.success(msg) if s else st.error(msg)
                        if s:
                            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown(styles.render_section_title("Low Stock Alert Monitor",
        icons.get_icon("alert_triangle", 16, t["danger"])), unsafe_allow_html=True)

    alerts = [p for p in products if p["stock_alert"] != "-"]
    if alerts:
        df_alert = pd.DataFrame(alerts)[
            ["product_id","name","category","quantity","min_stock","restock_qty","stock_alert"]
        ]
        st.dataframe(df_alert, use_container_width=True, hide_index=True)
    else:
        st.markdown(f"""
            <div class="sims-card" style="text-align:center;padding:28px;">
                {icons.get_icon("audit",36,t["success"])}
                <div style="color:{t['success']};font-weight:600;margin-top:10px;">
                    ✨ All inventory stock levels are healthy!
                </div>
            </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
#  5. USER MANAGEMENT (Admin only)
# ──────────────────────────────────────────────────────────────
elif page == "User Management" and role == "Admin":
    st.markdown(styles.render_section_title("User Account Management",
        icons.get_icon("users", 20, t["accent"])), unsafe_allow_html=True)

    users = db.get_all_users()

    col_u1, col_u2 = st.columns([1.6, 1])

    with col_u1:
        st.markdown(f"<div style='font-weight:600;color:{t['text_heading']};margin-bottom:8px;'>"
                    f"Registered Accounts ({len(users)})</div>", unsafe_allow_html=True)
        if users:
            st.dataframe(
                pd.DataFrame(users)[["user_id","full_name","role","dob","email"]],
                use_container_width=True, hide_index=True,
            )

    with col_u2:
        with st.expander("➕  Create New Account", expanded=True):
            with st.form("add_user_form"):
                new_role = st.selectbox("Role", ["Admin","Store Manager","Sales Staff"])
                prefix = "A" if new_role == "Admin" else ("M" if new_role == "Store Manager" else "S")
                preview_id = db.generate_user_id(prefix)
                st.caption(f"Auto-generated ID: **`{preview_id}`**")

                u_name  = st.text_input("Full Name")
                u_dob   = st.text_input("Date of Birth (DD/MM/YYYY)", placeholder="10/10/2000")
                u_email = st.text_input("Email", placeholder="user@sims.com")
                u_pass  = st.text_input("Password", type="password", help="Min 6 chars (Upper, Lower, Digit)")

                if st.form_submit_button("Create Account", type="primary", use_container_width=True):
                    s, msg = db.add_user(u_name, new_role, u_dob, u_email, u_pass, user_id)
                    if s:
                        st.success(f"User created! ID: **{msg}**")
                        st.rerun()
                    else:
                        st.error(msg)

        st.divider()

        with st.expander("🗑️  Delete Account"):
            del_uid = st.selectbox("Select User ID",
                ["Select..."] + [u["user_id"] for u in users if u["user_id"] != user_id])
            if del_uid != "Select...":
                target_u = next((u for u in users if u["user_id"] == del_uid), None)
                confirm_pass = ""
                if target_u and target_u["role"] == "Admin":
                    confirm_pass = st.text_input("Confirm Admin Password", type="password")
                if st.button("Delete Account", type="primary"):
                    s, msg = db.delete_user(del_uid, user_id, confirm_pass)
                    st.success(msg) if s else st.error(msg)
                    if s:
                        st.rerun()


# ──────────────────────────────────────────────────────────────
#  6. TRANSACTIONS
# ──────────────────────────────────────────────────────────────
elif page == "Transactions":
    st.markdown(styles.render_section_title("Sales Transaction History & Invoice Generator",
        icons.get_icon("transactions", 20, t["accent"])), unsafe_allow_html=True)

    txs = db.get_all_transactions()
    if txs:
        total_rev = sum(float(tx["total_price"]) for tx in txs)

        # Summary row
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(styles.render_kpi("Total Transactions", str(len(txs)), "",
                icons.get_icon("transactions", 18, t["accent"])), unsafe_allow_html=True)
        with sc2:
            st.markdown(styles.render_kpi("Total Revenue", f"${total_rev:,.2f}", "",
                icons.get_icon("currency", 18, t["success"])), unsafe_allow_html=True)
        with sc3:
            avg = total_rev / len(txs) if txs else 0
            st.markdown(styles.render_kpi("Avg per Transaction", f"${avg:,.2f}", "",
                icons.get_icon("trending_up", 18, t["accent3"])), unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # ── Invoice Generator Tool ──
        with st.container(border=True):
            st.markdown(f"#### {icons.get_icon('reports', 16, t['accent'])} Generate Invoice PDF for Historical Sale", unsafe_allow_html=True)
            
            unique_tids = list(dict.fromkeys(t["trans_id"] for t in txs))
            
            gen_col1, gen_col2 = st.columns([3, 1])
            selected_tid = gen_col1.selectbox("Select Transaction Reference ID:", unique_tids, key="tx_sel_id")
            
            if gen_col2.button("🧾 Generate Invoice PDF", type="primary", use_container_width=True):
                inv_data = db.get_invoice_data_by_trans_id(selected_tid)
                if inv_data:
                    pdf_bytes, pdf_path = pdf_generator.generate_invoice_pdf(inv_data)
                    st.session_state.hist_inv = inv_data
                    st.session_state.hist_pdf_bytes = pdf_bytes
                    st.session_state.hist_pdf_path = pdf_path
                    st.toast(f"✅ Generated Invoice PDF: {pdf_path}", icon="💾")
                else:
                    st.error(f"Transaction ID {selected_tid} not found.")

            if "hist_inv" in st.session_state and st.session_state.hist_inv:
                h_inv = st.session_state.hist_inv
                h_tid = h_inv["items"][0]["trans_id"] if h_inv.get("items") else "T10001"
                
                st.html(styles.render_invoice_card_html(h_inv))

                hic1, hic2, hic3 = st.columns([1.5, 1.5, 1])
                with hic1:
                    if "hist_pdf_bytes" in st.session_state:
                        st.download_button(
                            "📥 Download PDF Invoice",
                            data=st.session_state.hist_pdf_bytes,
                            file_name=f"Invoice_{h_tid}.pdf",
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True,
                        )
                with hic2:
                    st.components.v1.html(
                        """<button onclick="window.parent.print()"
                            style="background:linear-gradient(135deg,#4f46e5,#7c3aed); color:#ffffff;
                            font-family:'Inter',sans-serif; font-weight:700; border:none; padding:12px 24px;
                            border-radius:12px; cursor:pointer; width:100%; height:46px; font-size:15px;
                            box-shadow:0 4px 14px rgba(79,70,229,0.3); transition:all 0.2s ease;">
                            🖨️ Print Receipt
                        </button>""",
                        height=56,
                    )
                with hic3:
                    if st.button("✕ Close Preview", key="btn_close_hist_inv", use_container_width=True):
                        del st.session_state.hist_inv
                        if "hist_pdf_bytes" in st.session_state:
                            del st.session_state.hist_pdf_bytes
                        st.rerun()

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(txs), use_container_width=True, hide_index=True)
    else:
        st.markdown(f"""
            <div class="sims-card" style="text-align:center;padding:40px 20px;">
                {icons.get_icon("transactions",48,t["text_sub"])}
                <div style="color:{t['text_sub']};margin-top:14px;">No transaction records found.</div>
            </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
#  7. REPORTS & ANALYTICS
# ──────────────────────────────────────────────────────────────
elif page in ["Reports", "Reports & Analytics"]:
    st.markdown(styles.render_section_title("Reports & Analytics",
        icons.get_icon("reports", 20, t["accent"])), unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📦  Inventory Report",
        "💵  Sales Summary",
        "🏆  Product Performance",
    ])

    with tab1:
        inv_data = db.get_inventory_report_data()
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown(styles.render_kpi("Total Products", str(inv_data["total_products"]), "",
                icons.get_icon("products",18,t["accent"])), unsafe_allow_html=True)
        with rc2:
            st.markdown(styles.render_kpi("Total Units", f"{inv_data['total_items']:,}", "",
                icons.get_icon("box",18,t["accent3"])), unsafe_allow_html=True)
        with rc3:
            st.markdown(styles.render_kpi("Valuation", f"${inv_data['total_valuation']:,.2f}", "",
                icons.get_icon("currency",18,t["success"])), unsafe_allow_html=True)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        if inv_data["products"]:
            st.dataframe(
                pd.DataFrame(inv_data["products"])[
                    ["product_id","name","category","price","quantity","min_stock"]
                ],
                use_container_width=True, hide_index=True,
            )

    with tab2:
        dc1, dc2 = st.columns(2)
        s_date = dc1.text_input("Start Date (DD/MM/YYYY)", value="01/07/2026")
        e_date = dc2.text_input("End Date (DD/MM/YYYY)",   value="31/07/2026")

        sales_data = db.get_sales_report_data(s_date, e_date)

        rs1, rs2, rs3, rs4 = st.columns(4)
        with rs1:
            st.markdown(styles.render_kpi("Period Transactions", str(sales_data["count"]), "",
                icons.get_icon("transactions",16,t["accent"])), unsafe_allow_html=True)
        with rs2:
            st.markdown(styles.render_kpi("Units Sold", str(sales_data["total_qty"]), "",
                icons.get_icon("box",16,t["accent3"])), unsafe_allow_html=True)
        with rs3:
            st.markdown(styles.render_kpi("Revenue", f"${sales_data['total_revenue']:,.2f}", "",
                icons.get_icon("currency",16,t["success"])), unsafe_allow_html=True)
        with rs4:
            avg_s = sales_data["total_revenue"] / sales_data["count"] if sales_data["count"] else 0
            st.markdown(styles.render_kpi("Avg per Sale", f"${avg_s:,.2f}", "",
                icons.get_icon("trending_up",16,t["accent"])), unsafe_allow_html=True)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        if sales_data["transactions"]:
            st.dataframe(pd.DataFrame(sales_data["transactions"]),
                         use_container_width=True, hide_index=True)
        else:
            st.info("No transactions found for selected date range.")

    with tab3:
        perf_data = db.get_performance_report_data()
        if perf_data:
            df_perf = pd.DataFrame(perf_data)
            palette = (
                ["#6366f1","#7c3aed","#2563eb","#059669","#d97706","#dc2626"]
                if is_light else
                ["#818cf8","#a78bfa","#60a5fa","#34d399","#fbbf24","#f87171"]
            )
            if "product_name" in df_perf.columns and "total_revenue" in df_perf.columns:
                fig_perf = px.bar(
                    df_perf.sort_values("total_revenue", ascending=False).head(10),
                    x="product_name", y="total_revenue",
                    color="product_name",
                    color_discrete_sequence=palette,
                    labels={"product_name":"Product","total_revenue":"Revenue ($)"},
                )
                fig_perf.update_layout(
                    **styles.get_plotly_layout(t),
                    height=360, showlegend=False,
                    xaxis_tickangle=-25,
                )
                fig_perf.update_traces(
                    hovertemplate="<b>%{x}</b><br>$%{y:,.2f}<extra></extra>",
                )
                st.plotly_chart(fig_perf, use_container_width=True)

            st.dataframe(df_perf, use_container_width=True, hide_index=True)
        else:
            st.info("No performance data available yet.")


# ──────────────────────────────────────────────────────────────
#  8. AUDIT LOGS
# ──────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────
#  8. AUDIT LOGS
# ──────────────────────────────────────────────────────────────
elif page == "Audit Logs" and role == "Admin":
    st.markdown(styles.render_section_title("Security Audit Trail",
        icons.get_icon("audit", 20, t["accent"])), unsafe_allow_html=True)

    logs = db.get_audit_logs()
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
    else:
        st.info("No audit events recorded yet.")


# ──────────────────────────────────────────────────────────────
#  8.5. BACKUP & RESTORE
# ──────────────────────────────────────────────────────────────
elif page == "Backup & Restore" and role == "Admin":
    st.markdown(styles.render_section_title("Backup & Restore Engine",
        icons.get_icon("database", 20, t["accent"])), unsafe_allow_html=True)

    tab_backup, tab_xampp = st.tabs([
        "💾 SQL Backup & Restore",
        "🐬 XAMPP / MariaDB Engine",
    ])

    with tab_backup:
        bc1, bc2 = st.columns(2)

        with bc1:
            with st.container(border=True):
                st.markdown(f"#### {icons.get_icon('reports', 16, t['accent'])} Export Database SQL Dump", unsafe_allow_html=True)
                st.markdown(
                    "Generate and download a complete, standalone `.sql` backup file containing all current "
                    "**Users**, **Products**, **Transactions**, and **Audit Logs**."
                )

                sql_dump_str = db.export_sql_dump()
                timestamp_fn = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                st.download_button(
                    "💾 Download SQL Backup (.sql)",
                    data=sql_dump_str,
                    file_name=f"sims_backup_{timestamp_fn}.sql",
                    mime="application/sql",
                    type="primary",
                    use_container_width=True,
                )

                st.caption("Matches both SQLite and MySQL/MariaDB schema formats.")

        with bc2:
            with st.container(border=True):
                st.markdown(f"#### {icons.get_icon('stock', 16, t['accent'])} Restore Database from SQL Dump", unsafe_allow_html=True)
                st.markdown(
                    "Upload a previously exported `.sql` dump file to restore system state. "
                    "**Warning:** Restoring will replace existing table data."
                )

                uploaded_sql = st.file_uploader("Choose a .sql dump file to restore:", type=["sql", "txt"])

                if uploaded_sql is not None:
                    sql_bytes = uploaded_sql.read()
                    sql_text_content = sql_bytes.decode("utf-8", errors="ignore")
                    
                    st.warning(f"⚠️ Selected dump file: `{uploaded_sql.name}` ({len(sql_bytes):,} bytes)")

                    if st.button("⚡ Confirm & Execute Database Restore", type="primary", use_container_width=True):
                        res_ok, res_msg = db.restore_sql_dump(sql_text_content, user_id)
                        if res_ok:
                            st.success(res_msg)
                            st.toast("✅ Database restore successful!", icon="💾")
                            st.rerun()
                        else:
                            st.error(res_msg)

    with tab_xampp:
        st.markdown(styles.render_section_title("XAMPP MySQL / MariaDB Integration",
            icons.get_icon("database", 16, t["accent"])), unsafe_allow_html=True)

        st.info(f"""
            **Active Engine:** `{db_info['engine']}`
            **Host:** `{db_info['host']}` | **Port:** `{db_info['port']}` | **User:** `{db_info['user']}`
            **Database:** `{db_info['database']}`
        """)

        xc1, xc2 = st.columns(2)
        with xc1:
            with st.container(border=True):
                st.markdown(f"#### {icons.get_icon('database', 16, t['accent'])} Import to phpMyAdmin",
                            unsafe_allow_html=True)
                st.markdown("1. Open XAMPP and start **MySQL**.")
                st.markdown("2. Open [http://localhost/phpmyadmin](http://localhost/phpmyadmin).")
                st.markdown("3. Create `sims_db` and import the SQL backup file.")

                sql_dump_php = db.export_sql_dump()
                st.download_button(
                    "📄 Download phpMyAdmin Dump (.sql)",
                    data=sql_dump_php,
                    file_name="sims_db.sql",
                    mime="application/sql",
                    type="secondary",
                    use_container_width=True,
                )

        with xc2:
            with st.container(border=True):
                st.markdown(f"#### {icons.get_icon('activity', 16, t['accent'])} Test Connection",
                            unsafe_allow_html=True)
                if st.button("🔄 Test XAMPP MySQL Connection", use_container_width=True):
                    db_type = db.get_active_db_type()
                    if "MySQL" in db_type:
                        st.success("🟢 Successfully connected to XAMPP MariaDB (`sims_db`)!")
                    else:
                        st.warning(
                            "ℹ️ XAMPP MySQL not running. System using SQLite3 (`sims.db`). "
                            "Start MySQL in XAMPP to switch engines."
                        )


# ──────────────────────────────────────────────────────────────
#  9. MY PROFILE
# ──────────────────────────────────────────────────────────────
elif page == "My Profile":
    st.markdown(styles.render_section_title("My Profile",
        icons.get_icon("profile", 20, t["accent"])), unsafe_allow_html=True)

    user_info = db.get_user_by_id(user_id)

    pc1, pc2 = st.columns(2)

    with pc1:
        st.markdown(f"""
            <div class="sims-card">
                <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">
                    <div style="width:60px;height:60px;border-radius:16px;
                        background:linear-gradient(135deg,{t['accent2']},{t['accent3']});
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.6rem;font-weight:900;color:#fff;">
                        {user_info['full_name'][0].upper()}
                    </div>
                    <div>
                        <div style="font-weight:800;font-size:1.15rem;color:{t['text_heading']};">
                            {user_info['full_name']}
                        </div>
                        <span class="badge badge-indigo">{user_info['role']}</span>
                    </div>
                </div>
                <div style="display:grid;gap:10px;">
                    <div style="display:flex;justify-content:space-between;padding:10px 0;
                        border-bottom:1px solid {t['divider']};">
                        <span style="color:{t['text_muted']};font-size:.85rem;">User ID</span>
                        <code style="color:{t['accent']};font-size:.85rem;">{user_info['user_id']}</code>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:10px 0;
                        border-bottom:1px solid {t['divider']};">
                        <span style="color:{t['text_muted']};font-size:.85rem;">Date of Birth</span>
                        <span style="color:{t['text_main']};font-size:.85rem;">{user_info['dob']}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:10px 0;
                        border-bottom:1px solid {t['divider']};">
                        <span style="color:{t['text_muted']};font-size:.85rem;">Email</span>
                        <span style="color:{t['text_main']};font-size:.85rem;">{user_info['email']}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:10px 0;">
                        <span style="color:{t['text_muted']};font-size:.85rem;">Role</span>
                        <span style="color:{t['accent']};font-size:.85rem;font-weight:600;">{user_info['role']}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with pc2:
        st.markdown(f"""
            <div style="font-weight:600;color:{t['text_heading']};margin-bottom:12px;">
                {icons.get_icon("profile",16,t["accent"])} Edit Profile
            </div>
        """, unsafe_allow_html=True)

        with st.form("edit_profile_form"):
            n_name  = st.text_input("Full Name",      value=user_info["full_name"])
            n_dob   = st.text_input("Date of Birth",  value=user_info["dob"])
            n_email = st.text_input("Email Address",  value=user_info["email"])
            st.divider()
            st.markdown(f"<div style='font-size:.85rem;color:{t['text_muted']};margin-bottom:6px;'>"
                        f"Change Password (leave blank to keep current)</div>", unsafe_allow_html=True)
            c_pass  = st.text_input("Current Password", type="password")
            n_pass  = st.text_input("New Password",     type="password")

            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                succ, msg = db.update_user_profile(
                    user_id=user_id,
                    full_name=n_name,
                    dob=n_dob,
                    email=n_email,
                    new_pass=n_pass if n_pass else None,
                    current_pass=c_pass if c_pass else None,
                )
                if succ:
                    st.success(msg)
                    st.session_state.user = db.get_user_by_id(user_id)
                    st.rerun()
                else:
                    st.error(msg)

# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
st.markdown(f"""
    <div style="border-top:1px solid {t['divider']};padding-top:16px;
        display:flex;justify-content:space-between;align-items:center;
        font-size:.78rem;color:{t['text_sub']};">
        <span>
            {icons.get_icon("sims_logo",18)} &nbsp;
            <strong style="color:{t['text_muted']};">SIMS Enterprise v2.0</strong>
            &nbsp;·&nbsp; Stock &amp; Inventory Management System
        </span>
        <span>
            {icons.get_icon("database",13,db_eng_color)} &nbsp;
            <span style="color:{db_eng_color};">{db_info['engine']}</span>
            &nbsp;·&nbsp; {datetime.now().strftime('%d %b %Y')}
        </span>
    </div>
""", unsafe_allow_html=True)
