import uuid
import datetime
from database import get_db_connection

def generate_invoice_number():
    """Generates a unique invoice number."""
    now = datetime.datetime.now()
    return f"INV-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

def generate_sku(category: str, name: str) -> str:
    """Simple SKU generator based on category and name."""
    cat_prefix = category[:3].upper() if category else "GEN"
    name_prefix = name[:3].upper() if name else "PRD"
    unique_id = uuid.uuid4().hex[:4].upper()
    return f"{cat_prefix}-{name_prefix}-{unique_id}"

def log_audit(username: str, action: str):
    """Log an action to the audit_logs table."""
    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')
    ip_address = "127.0.0.1" # Hardcoded for localhost as per requirements
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audit_logs (user, date, time, action, ip_address)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, date_str, time_str, action, ip_address))
