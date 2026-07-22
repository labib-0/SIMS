import sqlite3
from contextlib import contextmanager
import os
from config import DB_PATH
from utils.auth import encrypt_username, hash_password

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create Tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username_encrypted TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                date_of_birth TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                contact_info TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                sku TEXT UNIQUE NOT NULL,
                barcode TEXT UNIQUE,
                purchase_price REAL NOT NULL,
                selling_price REAL NOT NULL,
                current_stock INTEGER NOT NULL,
                minimum_stock INTEGER NOT NULL,
                supplier TEXT,
                description TEXT,
                image_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                total_amount REAL NOT NULL,
                tax_amount REAL NOT NULL,
                discount_amount REAL NOT NULL,
                final_amount REAL NOT NULL,
                sale_date TEXT DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                change_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                date TEXT DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                notes TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                action TEXT NOT NULL,
                ip_address TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                date TEXT DEFAULT CURRENT_TIMESTAMP,
                size TEXT
            )
        ''')
        
        # Check if admin exists
        encrypted_admin = encrypt_username("admin")
        cursor.execute("SELECT id FROM users WHERE username_encrypted = ?", (encrypted_admin,))
        if not cursor.fetchone():
            hashed_pw = hash_password("admin123")
            # Default DOB for admin: 2000-01-01
            cursor.execute('''
                INSERT INTO users (username_encrypted, password_hash, role, date_of_birth, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (encrypted_admin, hashed_pw, "Admin", "2000-01-01", 1))
            
        # Seed 10 default categories if none exist
        cursor.execute("SELECT COUNT(id) FROM categories")
        if cursor.fetchone()[0] == 0:
            default_categories = [
                "Electronics", "Clothing", "Food & Beverage", "Furniture", 
                "Health & Beauty", "Automotive", "Toys & Games", 
                "Office Supplies", "Hardware", "Miscellaneous"
            ]
            for cat in default_categories:
                cursor.execute("INSERT INTO categories (name) VALUES (?)", (cat,))

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
