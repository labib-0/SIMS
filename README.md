# Stock and Inventory Management System (SIMS) 📦

[![Language: C](https://img.shields.io/badge/Language-C-00599C.svg?style=flat&logo=c)](https://en.wikipedia.org/wiki/C_(programming_language))
[![Platform: Mac & Windows](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%2011-blue.svg)](https://github.com/labib-0/SIMS_C)
[![Algorithm: Binary Search](https://img.shields.io/badge/Search-Binary%20Search%20O(log%20N)-brightgreen.svg)](https://github.com/labib-0/SIMS_C)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A high-performance, modular, menu-driven command-line **Stock and Inventory Management System (SIMS)** written in pure **C**. Developed as part of the **Software Development Capstone Project (CEP2)** at Daffodil International University.

---

## 🚀 System Architecture & Key Features

### 🔐 1. Role-Based Access Control (RBAC)
- **Administrator (`A`)**:
  - **User Management**: Compact user lifecycle operations (`Add User`, `Delete User`, `View All Users`).
  - **Product Management**: Complete CRUD operations (`Add`, `Update`, `Delete`, `View`, `Search`).
  - **Stock Management**: Direct inventory table view with dynamic stock alert statuses and instant restocking.
  - **POS Sales Processing**: Multi-item shopping cart sales and itemized invoice receipt generation.
  - **Reports & Security**: Full business reports, system data backups/restores, audit log viewing, and profile management.
- **Store Manager (`M`)**:
  - **Product Management**: Complete product catalog management (`Add`, `Update`, `Delete`, `View`, `Search`).
  - **Stock Replenishment Requests**: Submit restock requests (`Staff Reported` alerts for Admin approval).
  - **Sales & Reports**: View sales transaction history, inventory valuation, and sales summary reports.
  - **My Profile**: View and update account credentials.
- **Sales Staff (`S`)**:
  - **POS Sales Processing**: Interactive multi-item shopping cart with live `TOTAL AMOUNT SO FAR` and invoice generation.
  - **Catalog Access**: View and search products in the store catalog.
  - **Restock Requests**: Flag low-stock items for manager/admin replenishment.
  - **My Profile**: View and update personal profile details.

---

### 🛒 2. POS Multi-Item Shopping Cart & Invoicing
- **Interactive Shopping Cart**: Add multiple products and quantities to a live cart with real-time stock availability checks.
- **Live Amount Tracker**: Displays `TOTAL AMOUNT SO FAR : $XXX.XX` as items are added or updated in the cart.
- **Itemized Sales Invoice**: Instant checkout (`1`) deducts stock from `products.csv`, logs itemized transactions to `transactions.csv`, and prints a professional sales receipt on terminal.

---

### 📦 3. Stock Management & Alert System
- **Direct Table Listing**: Formatted screen displaying `ID`, `Product Name`, `Category`, `Price ($)`, `Stock Qty`, and `Stock Alert`.
- **Dynamic System Alerts**:
  - `System Low Stock`: Triggered automatically when `Stock Qty <= Min Qty`.
  - `System Out of Stock`: Triggered when `Stock Qty <= 0`.
  - `Staff Reported`: Triggered when staff/manager manually submits a reorder request.

---

### 🔑 4. Multi-Factor Security & Profile Management
- **Email Format Validation**: Ensures valid email addresses with `@` and `.` domain structure validation.
- **4-Tier Password Recovery (`Forgot Password`)**: Requires multi-factor verification of **User ID**, **Full Name**, **Date of Birth (DOB)**, and **Email Address** before resetting password.
- **My Profile (`View & Edit`)**: Dedicated profile section on all dashboards allowing users to view details and edit Full Name, DOB, Email, or Password.
- **Standardized Navigation**: `0. Logout` on main dashboards, `0. Back` on submenus, and `0. Exit` on the startup menu.
- **Crisp UX Transitions**: Ultra-fast 0.5-second (`500ms`) smooth screen transitions (`usleep(500000)` / `Sleep(500)`).

---

## 🔑 Default System Credentials

Upon initial launch, the system automatically initializes default accounts in `users.csv` if no records exist:

| Role | User ID | Password | Date of Birth | Email |
|---|---|---|---|---|
| **Administrator** | `A100` | `Admin123` | `01/01/2000` | `admin@sims.com` |
| **Store Manager** | `M100` | `Asad123` | `10/10/2000` | `asad@sims.com` |
| **Sales Staff** | `S100` | `Masuk123` | `10/10/2000` | `masuk@sims.com` |

---

## 🏗️ Project Architecture & File Structure

The project follows a clean, decoupled, multi-module C architecture:

```text
SIMS_C/
├── main.c           # Program entry point, database initializers, & roleMenu router
├── utility.c        # Centralized utilities, date/time, usleep delay, & Binary Search
├── auth.c           # Password hashing, validation, login, forgot password, & My Profile
├── admin.c          # Administrator Dashboard & User Management features
├── manager.c        # Store Manager Dashboard
├── staff.c          # Sales Staff Dashboard
├── inventory.c      # Product CRUD, stock management, stock alerts, & restock requests
├── transaction.c    # POS multi-item shopping cart, checkout invoicing, & sales history
├── reports.c        # Inventory, sales summary, product performance reports, & audit log
│
├── users.csv        # Registered users database (UserID,FullName,Role,DOB,Email,Password)
├── products.csv     # Product inventory database (ProductID,Name,Category,Price,Quantity,MinStock,RestockQty,StockAlert)
├── transactions.csv # Sales transaction log (TransactionID,Date,Time,ProductID,ProductName,Quantity,UnitPrice,TotalPrice,SoldBy)
└── audit_log.txt    # Real-time system audit trail
```

---

## 💻 Building and Running the System

### Prerequisites
- Any standard C compiler (**GCC** or **Clang**).
- Cross-platform compatible with **macOS** and **Windows 11 / Linux**.

### 1. Compilation
Compile all modular source files using `gcc`:

```bash
gcc -Wall main.c utility.c auth.c inventory.c transaction.c reports.c admin.c manager.c staff.c -o sims
```

### 2. Execution
Run the compiled executable:

```bash
./sims
```

On Windows (Command Prompt / PowerShell):
```cmd
sims.exe
```

---

## 🎓 Academic & Team Information

- **Course Name**: Software Development Capstone Project (CEP2)
- **Project Name**: Stock and Inventory Management System
- **Semester**: Summer 2026
- **Batch**: 45 | **Section**: C1 | **Group**: 01 (`temp8`)
- **Institution**: Daffodil International University
- **Course Teacher**: Jafrin Iqbal Chowdhury (Lecturer)

### Team Members
| Sl. | Student Name | Student ID |
|---|---|---|
| 1. | **Labib Ul Hasan** | `252-35-031` |
| 2. | **Masuk Al Aff** | `252-35-099` |
| 3. | **Rim Akter** | `252-35-167` |

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
