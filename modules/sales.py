import streamlit as st
import pandas as pd
import datetime
from database import get_db_connection
from utils.helpers import generate_invoice_number, log_audit
from utils.export import generate_invoice_pdf
from utils.auth import encrypt_username

def init_cart():
    if 'cart' not in st.session_state:
        st.session_state.cart = []

def render_sales():
    st.title("🛒 Sales & POS")
    init_cart()
    
    col1, col2 = st.columns([2, 1])
    
    with get_db_connection() as conn:
        products_df = pd.read_sql_query("SELECT id, name, sku, selling_price, current_stock FROM products WHERE current_stock > 0", conn)
        
    with col1:
        st.subheader("Add to Cart")
        if not products_df.empty:
            with st.form("add_to_cart"):
                p_id = st.selectbox("Select Product", products_df['id'].tolist(), format_func=lambda x: f"{products_df[products_df['id'] == x]['name'].values[0]} - ${products_df[products_df['id'] == x]['selling_price'].values[0]:.2f}")
                qty = st.number_input("Quantity", min_value=1, step=1, value=1)
                
                if st.form_submit_button("Add"):
                    product = products_df[products_df['id'] == p_id].iloc[0]
                    if qty > product['current_stock']:
                        st.error(f"Not enough stock! Current stock is {product['current_stock']}")
                    else:
                        # Check if already in cart
                        found = False
                        for item in st.session_state.cart:
                            if item['id'] == p_id:
                                if item['qty'] + qty > product['current_stock']:
                                    st.error("Total quantity exceeds available stock!")
                                else:
                                    item['qty'] += qty
                                    item['total'] = item['qty'] * item['price']
                                    st.success("Updated cart.")
                                found = True
                                break
                        if not found:
                            st.session_state.cart.append({
                                'id': p_id,
                                'name': product['name'],
                                'price': product['selling_price'],
                                'qty': qty,
                                'total': qty * product['selling_price']
                            })
                            st.success("Added to cart.")
                        st.rerun()
        else:
            st.warning("No products available with stock > 0.")
            
    with col2:
        st.subheader("Shopping Cart")
        
        if not st.session_state.cart:
            st.info("Cart is empty.")
        else:
            cart_df = pd.DataFrame(st.session_state.cart)
            # Display cart
            for i, item in enumerate(st.session_state.cart):
                cols = st.columns([3, 1, 1, 1])
                cols[0].write(item['name'])
                cols[1].write(f"x{item['qty']}")
                cols[2].write(f"${item['total']:.2f}")
                if cols[3].button("❌", key=f"del_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
            
            subtotal = sum(item['total'] for item in st.session_state.cart)
            tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            discount = st.number_input("Discount ($)", min_value=0.0, value=0.0, step=1.0)
            
            tax_amount = subtotal * (tax_rate / 100)
            final_amount = subtotal + tax_amount - discount
            
            st.markdown("---")
            st.write(f"**Subtotal:** ${subtotal:.2f}")
            st.write(f"**Tax:** ${tax_amount:.2f}")
            st.write(f"**Discount:** ${discount:.2f}")
            st.markdown(f"### **Total: ${final_amount:.2f}**")
            
            if final_amount < 0:
                st.error("Total cannot be negative!")
            else:
                if st.button("Complete Sale", use_container_width=True, type="primary"):
                    invoice_num = generate_invoice_number()
                    
                    try:
                        with get_db_connection() as conn:
                            cursor = conn.cursor()
                            user = cursor.execute("SELECT id FROM users WHERE username_encrypted = ?", (encrypt_username(st.session_state.username),)).fetchone()
                            user_id = user[0] if user else 0
                            
                            # Insert Sale
                            cursor.execute("""
                                INSERT INTO sales (invoice_number, total_amount, tax_amount, discount_amount, final_amount, user_id)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (invoice_num, subtotal, tax_amount, discount, final_amount, user_id))
                            sale_id = cursor.lastrowid
                            
                            # Insert Sale Items & Update Stock
                            for item in st.session_state.cart:
                                cursor.execute("""
                                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_price)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (sale_id, item['id'], item['qty'], item['price'], item['total']))
                                
                                # Update stock
                                cursor.execute("UPDATE products SET current_stock = current_stock - ? WHERE id = ?", (item['qty'], item['id']))
                                
                                # Inventory history
                                cursor.execute("""
                                    INSERT INTO inventory_history (product_id, change_type, quantity, user_id, notes)
                                    VALUES (?, 'OUT', ?, ?, ?)
                                """, (item['id'], item['qty'], user_id, f"Sale {invoice_num}"))
                                
                        log_audit(st.session_state.username, f"Completed sale {invoice_num} for ${final_amount:.2f}")
                        st.success(f"Sale completed successfully! Invoice: {invoice_num}")
                        
                        # Generate PDF
                        sale_details = {
                            'invoice_number': invoice_num,
                            'sale_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'total_amount': subtotal,
                            'tax_amount': tax_amount,
                            'discount_amount': discount,
                            'final_amount': final_amount
                        }
                        
                        items_df = pd.DataFrame([{
                            'Product Name': item['name'],
                            'Quantity': item['qty'],
                            'Unit Price': item['price'],
                            'Total Price': item['total']
                        } for item in st.session_state.cart])
                        
                        pdf_bytes = generate_invoice_pdf(sale_details, items_df)
                        
                        st.download_button(
                            label="📥 Download Invoice PDF",
                            data=pdf_bytes,
                            file_name=f"{invoice_num}.pdf",
                            mime="application/pdf"
                        )
                        
                        # Clear cart
                        st.session_state.cart = []
                        # No rerun here to allow downloading PDF, user can click to clear manually or next tab click will refresh
                    except Exception as e:
                        st.error(f"Error completing sale: {e}")
