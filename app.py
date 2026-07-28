import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

import db
import styles
import pdf_generator

# Set Page Config
st.set_page_config(
    page_title="SIMS - Stock & Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database & Clean CSS
db.init_db()
styles.inject_custom_css()

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "cart" not in st.session_state:
    st.session_state.cart = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"
if "forgot_mode" not in st.session_state:
    st.session_state.forgot_mode = False
if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0

def logout():
    if st.session_state.user:
        db.log_action(st.session_state.user["user_id"], "Logged out")
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.cart = []
    st.session_state.current_page = "Dashboard"
    st.session_state.forgot_mode = False
    st.session_state.login_attempts = 0

# ==========================================
# AUTHENTICATION & LOGIN (ULTRA-CLEAN MINIMALIST)
# ==========================================

if not st.session_state.authenticated:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    col_l1, col_center, col_l2 = st.columns([1, 1.2, 1])

    with col_center:
        if not st.session_state.forgot_mode:
            st.markdown("""
                <div style="text-align: center; margin-bottom: 24px;">
            """, unsafe_allow_html=True)
            
            if os.path.exists("logo.png"):
                st.image("logo.png", width=110)

            st.markdown("""
                    <h2 class="clean-login-title">SIMS Enterprise</h2>
                    <div class="clean-login-sub">Stock & Inventory Management System</div>
                </div>
            """, unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                user_input = st.text_input("User ID or Email", placeholder="e.g. A100 or admin@sims.com", label_visibility="visible")
                password_input = st.text_input("Password", type="password", placeholder="••••••••", label_visibility="visible")
                
                st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
                login_btn = st.form_submit_button("Sign In", type="primary", use_container_width=True)

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

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            col_ft1, col_ft2 = st.columns(2)
            with col_ft1:
                if st.button("Forgot password?", key="btn_forgot_nav", use_container_width=True):
                    st.session_state.forgot_mode = True
                    st.rerun()
            with col_ft2:
                with st.popover("Demo Credentials"):
                    st.markdown("""
                        <div style="font-size: 0.85rem; color: #a1a1aa; line-height: 1.8;">
                            • <b>Admin</b>: <code>A100</code> / <code>Admin123</code><br>
                            • <b>Manager</b>: <code>M100</code> / <code>Asad123</code><br>
                            • <b>Staff</b>: <code>S100</code> / <code>Masuk123</code>
                        </div>
                    """, unsafe_allow_html=True)

        else:
            st.markdown("""
                <div style="text-align: center; margin-bottom: 24px;">
                    <h2 class="clean-login-title">Reset Password</h2>
                    <div class="clean-login-sub">Enter verification details to update credentials</div>
                </div>
            """, unsafe_allow_html=True)

            with st.form("forgot_form"):
                f_uid = st.text_input("User ID", placeholder="e.g. A100")
                f_name = st.text_input("Full Name", placeholder="e.g. Default Admin")
                f_dob = st.text_input("Date of Birth", placeholder="DD/MM/YYYY")
                f_email = st.text_input("Email Address", placeholder="admin@sims.com")
                f_new_pass = st.text_input("New Password", type="password", help="Min 6 chars (Upper, Lower, Digit)")

                st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
                reset_btn = st.form_submit_button("Reset Password", type="primary", use_container_width=True)

                if reset_btn:
                    success, msg = db.reset_password_forgot(f_uid, f_name, f_dob, f_email, f_new_pass)
                    if success:
                        st.success(msg)
                        st.session_state.forgot_mode = False
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("← Back to Sign In", use_container_width=True):
                st.session_state.forgot_mode = False
                st.rerun()

    st.stop()

# ==========================================
# MAIN APP (LOGGED IN DASHBOARD)
# ==========================================

current_user = st.session_state.user
role = current_user["role"]
user_id = current_user["user_id"]
full_name = current_user["full_name"]
db_info = db.get_db_info()

# SIDEBAR
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=70)

    st.markdown(f"""
        <div class="sidebar-user-card">
            <div style="font-weight: 700; font-size: 1rem; color: #ffffff;">{full_name}</div>
            <div style="font-size: 0.8rem; color: #a1a1aa;">ID: <code>{user_id}</code></div>
            <div style="margin-top: 8px; display: flex; gap: 6px; flex-wrap: wrap;">
                <span class="clean-badge clean-badge-yellow">{role}</span>
                <span class="clean-badge {"clean-badge-green" if db_info["is_xampp"] else "clean-badge-orange"}">
                    {"🟢 XAMPP MySQL" if db_info["is_xampp"] else "📁 SQLite3"}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.caption("NAVIGATION")

    nav_options = []
    if role == "Admin":
        nav_options = ["Dashboard", "POS Terminal", "Product Catalog", "Stock Operations", "User Management", "Transactions", "Reports", "Audit Logs", "My Profile"]
    elif role == "Store Manager":
        nav_options = ["Dashboard", "Product Catalog", "Restock Requests", "Transactions", "Reports", "My Profile"]
    else: # Sales Staff
        nav_options = ["Dashboard", "POS Terminal", "Product Catalog", "Restock Requests", "Transactions", "My Profile"]

    for opt in nav_options:
        icon = "📊" if opt == "Dashboard" else ("🛒" if "POS" in opt else ("📦" if "Catalog" in opt or "Product" in opt else ("🔁" if "Stock" in opt or "Restock" in opt else ("👥" if "User" in opt else ("📄" if "Trans" in opt else ("📈" if "Report" in opt else ("🛡️" if "Audit" in opt else "👤")))))))
        is_active = (st.session_state.current_page == opt)
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"{icon}  {opt}", key=f"nav_{opt}", use_container_width=True, type=btn_type):
            st.session_state.current_page = opt
            st.rerun()

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        logout()
        st.rerun()

# PAGE CONTENT ROUTER
page = st.session_state.current_page

# TOP HEADER
st.markdown(f"""
    <div class="sims-top-header">
        <div>
            <h1>SIMS Control Center</h1>
            <div style="color: #a1a1aa; font-size: 0.9rem; margin-top: 4px;">
                Session: <strong style="color:#ffffff;">{full_name} ({user_id})</strong> | Role: <strong style="color:#eab308;">{role}</strong> | 
                Engine: <strong style="color:{"#4ade80" if db_info["is_xampp"] else "#fb923c"};">{db_info['engine']}</strong>
            </div>
        </div>
        <div style="text-align: right; font-family: var(--font-mono); font-size: 0.85rem; color: #a1a1aa;">
            {datetime.now().strftime("%d %b %Y | %H:%M:%S")}
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 1. DASHBOARD PAGE
# ==========================================
if page == "Dashboard":
    products = db.get_all_products()
    transactions = db.get_all_transactions()
    users = db.get_all_users()
    logs = db.get_audit_logs()

    total_revenue = sum(float(t["total_price"]) for t in transactions)
    low_stock_count = sum(1 for p in products if p["stock_alert"] in ["System Low Stock", "System Out of Stock", "Staff Reported"])
    total_products = len(products)
    total_items = sum(int(p["quantity"]) for p in products)
    total_valuation = sum(float(p["price"]) * int(p["quantity"]) for p in products)

    # KPI TILES
    kpi_cols = st.columns(5)
    with kpi_cols[0]:
        st.markdown(styles.render_kpi("Total Sales", f"${total_revenue:,.2f}", f"{len(transactions)} Transactions"), unsafe_allow_html=True)
    with kpi_cols[1]:
        st.markdown(styles.render_kpi("Stock Alerts", f"{low_stock_count}", "Requires Attention"), unsafe_allow_html=True)
    with kpi_cols[2]:
        st.markdown(styles.render_kpi("Total Products", f"{total_products}", f"{total_items:,} Items in Stock"), unsafe_allow_html=True)
    with kpi_cols[3]:
        st.markdown(styles.render_kpi("Inventory Value", f"${total_valuation:,.2f}", "Total Stock Valuation"), unsafe_allow_html=True)
    with kpi_cols[4]:
        st.markdown(styles.render_kpi("Active Users", f"{len(users)}", "System Accounts"), unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # CHARTS ROW
    col_chart1, col_chart2 = st.columns([1.2, 1])

    with col_chart1:
        st.subheader("Inventory Distribution by Category")
        df_prod = pd.DataFrame(products)
        if not df_prod.empty:
            cat_df = df_prod.groupby("category")["quantity"].sum().reset_index()
            fig = px.pie(cat_df, values="quantity", names="category", hole=0.45,
                         color_discrete_sequence=px.colors.qualitative.Dark24)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#ffffff",
                              legend=dict(font=dict(color="#ffffff")))
            st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        st.subheader("Top Revenue Products")
        df_tx = pd.DataFrame(transactions)
        if not df_tx.empty:
            top_df = df_tx.groupby("product_name")["total_price"].sum().reset_index().sort_values("total_price", ascending=False).head(5)
            fig_bar = px.bar(top_df, x="product_name", y="total_price", color="total_price",
                             labels={"product_name": "Item", "total_price": "Revenue ($)"},
                             color_continuous_scale="Purples")
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#ffffff")
            st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("System Activity Stream")
    if logs:
        recent_logs = logs[:6]
        for l in recent_logs:
            st.markdown(f"• <code style='color:#eab308;'>[{l['timestamp']}]</code> **[{l['user_id']}]** {l['action']}", unsafe_allow_html=True)

# ==========================================
# 2. POS TERMINAL PAGE
# ==========================================
elif page == "POS Terminal":
    st.subheader("🛒 POS Terminal & Checkout")

    products = db.get_all_products()
    col_left, col_right = st.columns([1.6, 1])

    with col_left:
        st.markdown("### Select Items")
        
        search_kw = st.text_input("Search catalog...", placeholder="Search Product Name, ID, or Category...")
        
        filtered_p = [p for p in products if search_kw.lower() in p["product_id"].lower() or search_kw.lower() in p["name"].lower() or search_kw.lower() in p["category"].lower()]
        
        for p in filtered_p:
            in_cart_qty = sum(item["quantity"] for item in st.session_state.cart if item["product_id"] == p["product_id"])
            eff_avail = int(p["quantity"]) - in_cart_qty
            icon = styles.get_category_icon(p["category"])

            st.markdown(f"""
                <div class="kiosk-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 14px;">
                            <div style="font-size: 1.8rem; background: #27272a; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                                {icon}
                            </div>
                            <div>
                                <div style="font-weight: 700; font-size: 1.05rem; color: #ffffff;">{p['name']} <span style="font-size: 0.8rem; color:#a1a1aa;">({p['product_id']})</span></div>
                                <div style="font-size: 0.8rem; color: #eab308;">{p['category']}</div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 800; font-size: 1.2rem; color: #ffffff;">${float(p['price']):.2f}</div>
                            <div style="font-size: 0.8rem; color: #a1a1aa;">Stock: <strong>{eff_avail}</strong></div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            c_act1, c_act2 = st.columns([2, 1])
            with c_act1:
                if eff_avail > 0:
                    add_qty = st.number_input("Quantity", min_value=1, max_value=eff_avail, value=1, key=f"qty_{p['product_id']}", label_visibility="collapsed")
                else:
                    st.caption("Out of Stock")
            with c_act2:
                if eff_avail > 0:
                    if st.button("Add to Cart", key=f"add_{p['product_id']}", type="primary", use_container_width=True):
                        found = False
                        for item in st.session_state.cart:
                            if item["product_id"] == p["product_id"]:
                                item["quantity"] += add_qty
                                item["item_total"] = round(item["quantity"] * item["unit_price"], 2)
                                found = True
                                break
                        if not found:
                            st.session_state.cart.append({
                                "product_id": p["product_id"],
                                "name": p["name"],
                                "unit_price": float(p["price"]),
                                "quantity": add_qty,
                                "item_total": round(add_qty * float(p["price"]), 2)
                            })
                        st.toast(f"Added {add_qty}x {p['name']} to cart!", icon="🛒")
                        st.rerun()

    with col_right:
        st.markdown("### 🛒 Shopping Cart")
        
        if not st.session_state.cart:
            st.info("Cart is empty. Select items from the catalog.")
        else:
            cart_total = sum(item["item_total"] for item in st.session_state.cart)
            
            for idx, item in enumerate(st.session_state.cart):
                cc1, cc2, cc3 = st.columns([3, 1.5, 1])
                cc1.markdown(f"**{item['name']}**<br><small style='color:#a1a1aa;'>${item['unit_price']:.2f} x {item['quantity']}</small>", unsafe_allow_html=True)
                cc2.markdown(f"**${item['item_total']:.2f}**")
                if cc3.button("❌", key=f"del_cart_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                st.divider()

            st.markdown(f"""
                <div style="background: #18181b; border: 1px solid #27272a; border-radius: 14px; padding: 18px; text-align: center; margin: 16px 0;">
                    <div style="font-size: 0.85rem; color: #a1a1aa; text-transform: uppercase;">TOTAL AMOUNT</div>
                    <div style="font-family: var(--font-heading); font-size: 2rem; font-weight: 800; color: #eab308;">${cart_total:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.button("Clear Cart", use_container_width=True):
                st.session_state.cart = []
                st.rerun()

            if col_btn2.button("Checkout", type="primary", use_container_width=True):
                success, msg, invoice = db.process_pos_checkout(st.session_state.cart, user_id)
                if success:
                    pdf_bytes, pdf_path = pdf_generator.generate_invoice_pdf(invoice)
                    st.session_state.last_invoice = invoice
                    st.session_state.last_pdf_bytes = pdf_bytes
                    st.session_state.last_pdf_path = pdf_path
                    st.session_state.cart = []
                    st.toast(f"✅ Auto-saved PDF Invoice to PC: {pdf_path}", icon="💾")
                    st.rerun()
                else:
                    st.error(msg)

        # Invoice Modal & Printing
        if "last_invoice" in st.session_state and st.session_state.last_invoice:
            inv = st.session_state.last_invoice
            first_item = inv["items"][0] if inv.get("items") else {"trans_id": "T10001"}
            main_tid = first_item.get("trans_id", "T10001")

            st.markdown("---")
            st.markdown(f"### 🧾 Sales Invoice ({main_tid})")
            
            st.info(f"💾 **Auto-Saved PDF Location on PC:** `invoices/Invoice_{main_tid}.pdf`")

            st.markdown(f"""
                <div class="printable-invoice" style="background: #ffffff; color: #000000; border-radius: 14px; padding: 24px; font-family: var(--font-mono); margin-bottom: 16px;">
                    <h3 style="margin-top:0; text-align:center; color:#000;">SIMS SALES INVOICE</h3>
                    <p style="color:#333;"><strong>Date & Time:</strong> {inv['date']} {inv['time']}<br>
                    <strong>Cashier ID:</strong> {inv['sold_by']}<br>
                    <strong>Invoice Ref:</strong> {main_tid}</p>
                    <hr style="border: 1px solid #ddd;">
                    <table style="width:100%; border-collapse: collapse; text-align: left; color:#000;">
                        <thead>
                            <tr style="border-bottom: 2px solid #000;">
                                <th>Trans ID</th><th>Item</th><th>Qty</th><th>Price</th><th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(f"<tr><td>{i['trans_id']}</td><td>{i['product_name']}</td><td>{i['quantity']}</td><td>${i['unit_price']:.2f}</td><td>${i['item_total']:.2f}</td></tr>" for i in inv['items'])}
                        </tbody>
                    </table>
                    <hr style="border: 1px solid #ddd;">
                    <h3 style="text-align: right; color: #000;">GRAND TOTAL: ${inv['grand_total']:.2f}</h3>
                </div>
            """, unsafe_allow_html=True)

            inv_col1, inv_col2, inv_col3 = st.columns([1.2, 1.2, 1])

            with inv_col1:
                if "last_pdf_bytes" in st.session_state:
                    st.download_button(
                        label="📥 Download PDF Invoice",
                        data=st.session_state.last_pdf_bytes,
                        file_name=f"Invoice_{main_tid}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )

            with inv_col2:
                # Trigger Browser Print
                st.components.v1.html(
                    """
                    <button onclick="window.print()" style="background:#eab308; color:#000000; font-family:sans-serif; font-weight:bold; border:none; padding:10px; border-radius:10px; cursor:pointer; width:100%; height:42px; font-size:15px;">
                        🖨️ Print Receipt
                    </button>
                    """,
                    height=50
                )

            with inv_col3:
                if st.button("Close Modal", key="btn_close_inv_modal", use_container_width=True):
                    del st.session_state.last_invoice
                    if "last_pdf_bytes" in st.session_state:
                        del st.session_state.last_pdf_bytes
                    st.rerun()

# ==========================================
# 3. PRODUCT CATALOG PAGE
# ==========================================
elif page in ["Product Catalog", "Product Management"]:
    st.subheader("📦 Product Catalog")

    products = db.get_all_products()

    c_filt1, c_filt2, c_act = st.columns([2, 1.5, 1.5])
    
    with c_filt1:
        search_query = st.text_input("Search Product Catalog", placeholder="Search ID, Name, Category...")
    with c_filt2:
        status_filter = st.selectbox("Filter Stock Status", ["All Statuses", "System Low Stock", "System Out of Stock", "Staff Reported", "In Stock"])

    filtered = products
    if search_query:
        q = search_query.lower()
        filtered = [p for p in filtered if q in p["product_id"].lower() or q in p["name"].lower() or q in p["category"].lower()]
    if status_filter != "All Statuses":
        if status_filter == "In Stock":
            filtered = [p for p in filtered if p["stock_alert"] == "-"]
        else:
            filtered = [p for p in filtered if p["stock_alert"] == status_filter]

    if "flash_product_msg" in st.session_state and st.session_state.flash_product_msg:
        st.success(st.session_state.flash_product_msg)
        del st.session_state.flash_product_msg

    if role in ["Admin", "Store Manager"]:
        with st.expander("➕ Add New Product"):
            with st.form("add_product_form"):
                ap_col1, ap_col2 = st.columns(2)
                p_name = ap_col1.text_input("Product Name")
                p_cat = ap_col2.text_input("Category")
                p_price = ap_col1.number_input("Unit Price ($)", min_value=0.0, step=0.5)
                p_qty = ap_col2.number_input("Initial Quantity", min_value=0, step=1)
                p_min = ap_col1.number_input("Minimum Stock Level", min_value=0, step=1)

                add_submit = st.form_submit_button("Save Product", type="primary")
                if add_submit:
                    succ, msg = db.add_product(p_name, p_cat, p_price, p_qty, p_min, user_id)
                    if succ:
                        st.toast(f"Product '{p_name}' saved! Assigned ID: {msg}", icon="🎉")
                        st.session_state.flash_product_msg = f"🎉 Product '{p_name}' (Assigned Product ID: **{msg}**) has been successfully saved!"
                        st.rerun()
                    else:
                        st.error(msg)

    st.markdown(f"**Showing {len(filtered)} Products**")

    display_rows = []
    for p in filtered:
        display_rows.append({
            "ID": p["product_id"],
            "Item Name": p["name"],
            "Category": p["category"],
            "Price ($)": f"${float(p['price']):.2f}",
            "Stock Qty": p["quantity"],
            "Min Level": p["min_stock"],
            "Restock Req": p["restock_qty"],
            "Status": p["stock_alert"]
        })

    df_display = pd.DataFrame(display_rows)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    if role in ["Admin", "Store Manager"]:
        st.markdown("---")
        st.subheader("Product Actions")
        
        action_col1, action_col2 = st.columns(2)

        with action_col1:
            st.markdown("#### Edit Product Details")
            if products:
                selected_pid = st.selectbox("Select Product to Edit", [p["product_id"] for p in products], key="edit_pid_select")
                target_p = next((p for p in products if p["product_id"] == selected_pid), None)
                
                if target_p:
                    with st.form("edit_prod_form"):
                        e_name = st.text_input("New Name", value=target_p["name"])
                        e_cat = st.text_input("New Category", value=target_p["category"])
                        e_price = st.number_input("New Price ($)", value=float(target_p["price"]), min_value=0.0)
                        e_min = st.number_input("New Min Stock Level", value=int(target_p["min_stock"]), min_value=0)
                        
                        edit_submit = st.form_submit_button("Update Product Details", type="primary")
                        if edit_submit:
                            s, msg = db.update_product(selected_pid, e_name, e_cat, e_price, e_min, user_id)
                            if s:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

        with action_col2:
            if role == "Admin" and products:
                st.markdown("#### Delete Product")
                del_pid = st.selectbox("Select Product to Delete", ["Select..."] + [p["product_id"] for p in products], key="del_pid_select")
                if del_pid != "Select...":
                    if st.button(f"Confirm Delete Product {del_pid}", type="primary"):
                        s, msg = db.delete_product(del_pid, user_id)
                        if s:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

# ==========================================
# 4. STOCK OPERATIONS PAGE
# ==========================================
elif page in ["Stock Operations", "Restock Requests"]:
    st.subheader("🔁 Stock Operations & Replenishment")

    products = db.get_all_products()

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("### Restock Product")
        if products:
            r_pid_str = st.selectbox("Select Product to Restock", [p["product_id"] + " - " + p["name"] for p in products], key="restock_sel")
            if r_pid_str:
                pid = r_pid_str.split(" - ")[0]
                target_p = next((p for p in products if p["product_id"] == pid), None)
                if target_p:
                    st.info(f"Current Stock: **{target_p['quantity']}** | Status: `{target_p['stock_alert']}` | Pending Request Qty: **{target_p['restock_qty']}**")
                    
                    with st.form("restock_form"):
                        add_units = st.number_input("Units to Add", min_value=1, value=20)
                        restock_submit = st.form_submit_button("Add Stock Now", type="primary")
                        if restock_submit:
                            s, msg = db.restock_product(pid, add_units, user_id)
                            if s:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

    with col_r2:
        st.markdown("### Request Restock")
        if products:
            req_pid_str = st.selectbox("Select Product to Request Restock", [p["product_id"] + " - " + p["name"] for p in products], key="req_sel")
            if req_pid_str:
                req_pid = req_pid_str.split(" - ")[0]
                with st.form("request_form"):
                    req_units = st.number_input("Quantity to Request", min_value=1, value=25)
                    req_submit = st.form_submit_button("Submit Restock Request", type="primary")
                    if req_submit:
                        s, msg = db.request_restock(req_pid, req_units, user_id)
                        if s:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    st.markdown("---")
    st.markdown("### Low Stock Alert Monitor")
    alerts = [p for p in products if p["stock_alert"] != "-"]
    if alerts:
        st.dataframe(pd.DataFrame(alerts)[["product_id", "name", "category", "quantity", "min_stock", "restock_qty", "stock_alert"]], use_container_width=True, hide_index=True)
    else:
        st.success("✨ All inventory stock levels are healthy!")

# ==========================================
# 5. USER MANAGEMENT (ADMIN ONLY)
# ==========================================
elif page == "User Management" and role == "Admin":
    st.subheader("👥 User Account Lifecycle Management")

    users = db.get_all_users()

    col_u1, col_u2 = st.columns([1.5, 1])

    with col_u1:
        st.markdown("### Registered System Accounts")
        st.dataframe(pd.DataFrame(users)[["user_id", "full_name", "role", "dob", "email"]], use_container_width=True, hide_index=True)

    with col_u2:
        with st.expander("➕ Add New User Account", expanded=True):
            with st.form("add_user_form"):
                new_role = st.selectbox("Role", ["Admin", "Store Manager", "Sales Staff"])
                preview_id = db.generate_user_id("A" if new_role == "Admin" else ("M" if new_role == "Store Manager" else "S"))
                st.caption(f"Auto-generated User ID: **`{preview_id}`**")
                
                u_name = st.text_input("Full Name")
                u_dob = st.text_input("Date of Birth (DD/MM/YYYY)", placeholder="10/10/2000")
                u_email = st.text_input("Email Address", placeholder="user@sims.com")
                u_pass = st.text_input("Initial Password", type="password", help="Min 6 chars (Upper, Lower, Digit)")

                user_submit = st.form_submit_button("Create Account", type="primary")
                if user_submit:
                    s, msg = db.add_user(u_name, new_role, u_dob, u_email, u_pass, user_id)
                    if s:
                        st.success(f"User created successfully! Assigned User ID: **{msg}**")
                        st.rerun()
                    else:
                        st.error(msg)

        st.markdown("---")
        with st.expander("🗑️ Delete User Account"):
            del_uid = st.selectbox("Select User ID to Delete", ["Select..."] + [u["user_id"] for u in users if u["user_id"] != user_id])
            if del_uid != "Select...":
                target_u = next((u for u in users if u["user_id"] == del_uid), None)
                if target_u and target_u["role"] == "Admin":
                    confirm_pass = st.text_input("Confirm Your Admin Password", type="password")
                else:
                    confirm_pass = ""

                if st.button("Delete Account", type="primary"):
                    s, msg = db.delete_user(del_uid, user_id, confirm_pass)
                    if s:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

# ==========================================
# 6. TRANSACTIONS PAGE
# ==========================================
elif page == "Transactions":
    st.subheader("📄 Sales Order Transaction History")

    txs = db.get_all_transactions()
    if txs:
        total_rev = sum(float(t["total_price"]) for t in txs)
        st.markdown(f"**Total Transactions:** `{len(txs)}` | **Total Sales Revenue:** `${total_rev:,.2f}`")
        st.dataframe(pd.DataFrame(txs), use_container_width=True, hide_index=True)
    else:
        st.info("No transaction order records found.")

# ==========================================
# 7. REPORTS PAGE
# ==========================================
elif page in ["Reports", "Reports & Analytics"]:
    st.subheader("📈 Reports & Analytics")

    tab1, tab2, tab3 = st.tabs(["📦 Inventory Valuation Report", "💵 Sales Summary Report", "🏆 Product Performance Report"])

    with tab1:
        inv_data = db.get_inventory_report_data()
        st.markdown(f"**Total Products:** `{inv_data['total_products']}` | **Total Stock Units:** `{inv_data['total_items']}` | **Valuation:** `${inv_data['total_valuation']:,.2f}`")
        st.dataframe(pd.DataFrame(inv_data["products"])[["product_id", "name", "category", "price", "quantity", "min_stock"]], use_container_width=True, hide_index=True)

    with tab2:
        col_d1, col_d2 = st.columns(2)
        s_date = col_d1.text_input("Start Date (DD/MM/YYYY)", value="01/07/2026")
        e_date = col_d2.text_input("End Date (DD/MM/YYYY)", value="31/07/2026")
        
        sales_data = db.get_sales_report_data(s_date, e_date)
        st.markdown(f"**Period:** `{s_date}` to `{e_date}` | **Transactions:** `{sales_data['count']}` | **Units Sold:** `{sales_data['total_qty']}` | **Revenue:** `${sales_data['total_revenue']:,.2f}`")
        if sales_data["transactions"]:
            st.dataframe(pd.DataFrame(sales_data["transactions"]), use_container_width=True, hide_index=True)

    with tab3:
        perf_data = db.get_performance_report_data()
        st.dataframe(pd.DataFrame(perf_data), use_container_width=True, hide_index=True)

# ==========================================
# 8. AUDIT LOGS & XAMPP TOOLS PAGE
# ==========================================
elif page in ["Audit Logs", "Audit Logs & Security"] and role == "Admin":
    st.subheader("🛡️ Security Audit Trail & Dedicated Database (XAMPP)")

    tab_log, tab_xampp = st.tabs(["📋 Security Audit Trail", "🐬 XAMPP / MariaDB Database Management"])

    with tab_log:
        logs = db.get_audit_logs()
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)

    with tab_xampp:
        st.markdown("### 🐬 Dedicated XAMPP MySQL / MariaDB Integration")
        
        st.info(f"""
            **Current Active Database Engine:** `{db_info['engine']}`  
            • **Host:** `{db_info['host']}` | **Port:** `{db_info['port']}` | **User:** `{db_info['user']}`  
            • **Database Name:** `{db_info['database']}`
        """)

        col_x1, col_x2 = st.columns(2)

        with col_x1:
            st.markdown("#### 📥 Import to phpMyAdmin")
            st.markdown("If your instructor requires showing the database inside **XAMPP phpMyAdmin**:")
            st.markdown("1. Open **XAMPP Control Panel** and click **Start MySQL**.")
            st.markdown("2. Open [http://localhost/phpmyadmin](http://localhost/phpmyadmin).")
            st.markdown("3. Create database `sims_db` or import `sims_db.sql` file below.")

            if os.path.exists("sims_db.sql"):
                with open("sims_db.sql", "r", encoding="utf-8") as f:
                    sql_dump = f.read()
                st.download_button(
                    "📄 Download XAMPP SQL Dump (sims_db.sql)",
                    data=sql_dump,
                    file_name="sims_db.sql",
                    mime="application/sql",
                    type="primary"
                )

        with col_x2:
            st.markdown("#### ⚡ Re-test XAMPP MySQL Connection")
            st.markdown("Click below to test live connection to `localhost:3306`.")
            if st.button("🔄 Test Connection to XAMPP MySQL", use_container_width=True):
                db_type = db.get_active_db_type()
                if "MySQL" in db_type:
                    st.success(f"🟢 Successfully connected to dedicated XAMPP MariaDB (`sims_db`)!")
                else:
                    st.warning(f"ℹ️ XAMPP MySQL is not currently running on port 3306. System is safely running on embedded SQLite3 (`sims.db`). Start MySQL in XAMPP to connect!")

# ==========================================
# 9. MY PROFILE PAGE
# ==========================================
elif page == "My Profile":
    st.subheader("👤 User Profile")

    user_info = db.get_user_by_id(user_id)
    
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown(f"""
            <div style="background: #18181b; border: 1px solid #27272a; border-radius: 14px; padding: 20px;">
                <h4 style="margin-top:0; color:#eab308;">Profile Details</h4>
                <p><strong>User ID:</strong> <code>{user_info['user_id']}</code><br>
                <strong>Full Name:</strong> {user_info['full_name']}<br>
                <strong>Role:</strong> {user_info['role']}<br>
                <strong>Date of Birth:</strong> {user_info['dob']}<br>
                <strong>Email:</strong> {user_info['email']}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_p2:
        with st.form("edit_profile_form"):
            st.markdown("#### Edit Profile Information")
            n_name = st.text_input("Full Name", value=user_info["full_name"])
            n_dob = st.text_input("Date of Birth", value=user_info["dob"])
            n_email = st.text_input("Email Address", value=user_info["email"])
            st.markdown("---")
            st.markdown("#### Change Password (Optional)")
            c_pass = st.text_input("Current Password", type="password")
            n_pass = st.text_input("New Password", type="password", help="Leave blank to keep unchanged")

            prof_submit = st.form_submit_button("Save Profile Changes", type="primary")
            if prof_submit:
                succ, msg = db.update_user_profile(
                    user_id=user_id,
                    full_name=n_name,
                    dob=n_dob,
                    email=n_email,
                    new_pass=n_pass if n_pass else None,
                    current_pass=c_pass if c_pass else None
                )
                if succ:
                    st.success(msg)
                    st.session_state.user = db.get_user_by_id(user_id)
                    st.rerun()
                else:
                    st.error(msg)
