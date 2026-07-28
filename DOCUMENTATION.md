# SIMS - Stock & Inventory Management System 📦
## Complete Technical Documentation & Code Tutorial (XAMPP MySQL Integrated)

Welcome to the technical documentation and code tutorial for the **Stock & Inventory Management System (SIMS)** with **Dual Database Architecture (XAMPP MySQL / MariaDB + Embedded SQLite3 Fallback)**.

---

## 🐬 Dedicated XAMPP MySQL / MariaDB Integration

SIMS features a dual database engine architecture:
1. **XAMPP / MariaDB / MySQL Mode (`localhost:3306`)**:
   - Automatically connects to XAMPP MySQL server via `pymysql`.
   - Database name: `sims_db`.
   - Host: `localhost` | Port: `3306` | User: `root` | Password: `""`.
   - Creates `sims_db` database and tables (`users`, `products`, `transactions`, `audit_logs`) automatically.
2. **SQLite3 Embedded Fallback Mode (`sims.db`)**:
   - If XAMPP MySQL server is turned off, SIMS safely falls back to local embedded SQLite3 (`sims.db`), ensuring zero downtime!
3. **XAMPP phpMyAdmin Export Dump (`sims_db.sql`)**:
   - Generated a ready-to-import `sims_db.sql` database dump script in the workspace root.
   - Instructors can import `sims_db.sql` directly into phpMyAdmin (`http://localhost/phpmyadmin`) with 1 click!

---

## 📚 Categorized Function Reference

### 1. Database & Core Engine (`db.py`)

#### 🛠️ Dual Connection & Infrastructure
- `get_connection()`: Connects to XAMPP MySQL on `localhost:3306` if active, or falls back to embedded SQLite3 (`sims.db`).
- `get_active_db_type()`: Returns `"MySQL / MariaDB (XAMPP)"` or `"SQLite3 (Embedded)"`.
- `get_db_info()`: Returns diagnostic metadata (Host, Port, User, Database Name, Active Engine).
- `init_db()`: Initializes database tables (`users`, `products`, `transactions`, `audit_logs`) on MySQL or SQLite3.
- `seed_data()`: Seeds default accounts (`A100`, `M100`, `S100`, `S101`) and product catalog items when empty.
- `log_action(user_id, action)`: Inserts a security audit record into the active database `audit_logs` table.

#### 🔐 Security & Validation
- `hash_password(password)`: Hashes passwords using C-compatible 64-bit polynomial multiplication (`hash * 31 + char`).
- `validate_password(password)`: Enforces password rules (minimum 6 chars, >=1 uppercase, >=1 lowercase, >=1 digit).
- `validate_email(email)`: Validates email format using regex pattern matching (`user@domain.com`).

#### 👤 User Management Functions
- `get_user_by_id(user_id)`: Retrieves a single user record matching User ID.
- `get_all_users()`: Returns all registered system user records ordered by User ID.
- `authenticate_user(user_id_or_email, password_plain)`: Authenticates credentials against stored password hashes with explicit diagnostic error feedback.
- `generate_user_id(prefix)`: Generates auto-incrementing User IDs (`A101`, `M101`, `S102`).
- `add_user(full_name, role, dob, email, password_plain, created_by)`: Registers a new user account with email and password checks.
- `delete_user(user_id_to_delete, current_admin_id, admin_password_confirm)`: Deletes a user account with self-deletion and last admin safeguards.
- `reset_password_forgot(user_id, full_name, dob, email, new_password_plain)`: Resets a lost password after 4-tier multi-factor identity verification.
- `update_user_profile(user_id, full_name, dob, email, new_pass, current_pass)`: Updates profile credentials or password for an active user.

#### 📦 Product & Stock Management Functions
- `recalculate_stock_alert(qty, min_stock, current_alert)`: Computes stock alert status (`In Stock`, `System Low Stock`, `System Out of Stock`, `Staff Reported`).
- `get_all_products()`: Retrieves all inventory products with live stock alert status recalculations.
- `generate_product_id()`: Generates auto-incrementing Product IDs (`P001`, `P002`, `P016`).
- `add_product(name, category, price, quantity, min_stock, user_id)`: Inserts a new inventory product with non-negativity checks.
- `update_product(product_id, name, category, price, min_stock, user_id)`: Updates existing product details and recomputes stock alerts.
- `delete_product(product_id, user_id)`: Removes a product record from the active inventory database.
- `restock_product(product_id, add_quantity, user_id)`: Restocks inventory quantity for a target product and clears staff reorder flags.
- `request_restock(product_id, req_qty, user_id)`: Flags a product for reorder with requested quantity (`Staff Reported`).

#### 🛒 POS & Transaction Processing Functions
- `generate_transaction_id()`: Generates unique auto-incrementing transaction IDs (`T10001`, `T10002`).
- `process_pos_checkout(cart_items, user_id)`: Executes an atomic POS checkout, deducting stock, logging transactions, and returning receipt data.
- `get_all_transactions()`: Retrieves all historical sales transaction records.

#### 📈 Reports & Analytics Functions
- `get_inventory_report_data()`: Calculates product count, total stock items, and total inventory valuation.
- `get_sales_report_data(start_date_str, end_date_str)`: Filters sales transactions within a date range and computes total units sold and revenue.
- `get_performance_report_data()`: Computes total units sold and revenue per product, sorted by best sellers.
- `get_audit_logs()`: Returns all security audit log records ordered by latest ID.

---

## 🎓 How to Show XAMPP MySQL Integration to Your Instructor

1. **Step 1: Start XAMPP MySQL**
   - Open **XAMPP Control Panel** on your computer.
   - Click **Start** next to **MySQL** (and Apache if needed).
2. **Step 2: Open phpMyAdmin**
   - Open [http://localhost/phpmyadmin](http://localhost/phpmyadmin) in your web browser.
   - Click **Import** tab.
   - Select `sims_db.sql` from your project directory `/Users/asad/Documents/SIMS/sims_db.sql` (or click **Download XAMPP SQL Dump** inside SIMS Admin settings).
   - Click **Go** to import.
3. **Step 3: Launch SIMS Web Application**
   - Open terminal and run:
     ```bash
     streamlit run app.py
     ```
   - The top header and sidebar will display:  
     🟢 **Database Engine: MySQL / MariaDB (XAMPP)**  
     `Host: localhost | Port: 3306 | User: root | Database: sims_db`
