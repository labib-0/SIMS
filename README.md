# Stock & Inventory Management System (SIMS)

A complete, modern, desktop-style web application built with Python and Streamlit. Designed for robust stock and inventory management, suitable for university capstone projects.

## Features

- **Secure Authentication**: Role-based access control (Admin, Store Manager, Sales Staff) with max login attempts, lockout, and DOB-based password recovery. Custom username encryption and SHA256 password hashing.
- **Modern Dashboard**: High-level metrics and Plotly charts for sales trends and inventory distribution.
- **Product Management**: Complete CRUD operations for products. Automatically generate SKUs. Prevent deleting products with active stock.
- **Inventory Control**: Adjust stock in/out with detailed logging. Low stock alerts and historical tracking.
- **Point of Sale (POS)**: Shopping cart system with tax, discount calculations, automatic stock reduction, and printable PDF invoices.
- **Reports & Analytics**: Daily/Weekly/Monthly sales reports, top-selling products, and inventory valuation. Export to CSV, Excel, and PDF.
- **User Management**: Admins can create, activate, deactivate, and reset passwords for system users.
- **Backup & Restore**: One-click database backups and easy restoration to protect data integrity.
- **Comprehensive Audit Log**: Tracks every major action (logins, stock changes, sales) with timestamps and user information.

## Folder Structure

```
SIMS/
├── app.py                  # Main Streamlit application entry point
├── database.py             # Database initialization and schema
├── config.py               # Constants and app configurations
├── requirements.txt        # Dependencies
├── README.md               # Documentation
├── assets/                 # Static assets (logo, images)
├── database/               # Local SQLite database storage
├── modules/                # Feature-specific UI and logic components
│   ├── authentication.py
│   ├── dashboard.py
│   ├── products.py
│   ├── inventory.py
│   ├── sales.py
│   ├── reports.py
│   ├── users.py
│   ├── backup.py
│   ├── audit.py
│   └── settings.py
└── utils/                  # Reusable helper functions
    ├── auth.py
    ├── validators.py
    ├── helpers.py
    └── export.py
```

## Requirements

Ensure you have Python 3.9+ installed. The following packages are required:
- `streamlit`
- `pandas`
- `plotly`
- `fpdf`
- `openpyxl`

## Installation & Setup

1. **Clone or Download the Repository**
2. **Install Dependencies**
   Navigate to the project root and run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application**
   Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```
4. **Initial Login**
   On the first run, the database will automatically initialize and seed the default admin account:
   - **Username**: `admin`
   - **Password**: `admin123`
   - **Date of Birth**: `2000-01-01` (used for password reset)

## Screenshots Placeholder
*(Add your screenshots here: Dashboard, POS Terminal, Inventory view, etc.)*

## Future Improvements
- Barcode/QR Code scanning integration for POS.
- Email notifications for low stock alerts.
- Advanced predictive analytics for sales forecasting using Machine Learning.
- Supplier purchase order generation.
