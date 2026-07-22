import re

def is_valid_username(username: str) -> bool:
    """Check if username is alphanumeric and at least 3 chars."""
    if not username or len(username) < 3:
        return False
    return re.match(r"^[a-zA-Z0-9_]+$", username) is not None

def is_valid_password(password: str) -> bool:
    """Check if password is at least 6 chars, with upper, lower, and digit."""
    if not password or len(password) < 6:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit

def is_positive_number(value) -> bool:
    """Check if value is a positive number (float or int)."""
    try:
        val = float(value)
        return val >= 0
    except (ValueError, TypeError):
        return False

def validate_product_data(name, category, sku, purchase_price, selling_price, current_stock, minimum_stock):
    """Validate core product data fields."""
    errors = []
    if not name:
        errors.append("Product name is required.")
    if not category:
        errors.append("Category is required.")
    if not sku:
        errors.append("SKU is required.")
    if not is_positive_number(purchase_price):
        errors.append("Purchase price must be a positive number.")
    if not is_positive_number(selling_price):
        errors.append("Selling price must be a positive number.")
    if not is_positive_number(current_stock):
        errors.append("Current stock must be a positive number.")
    if not is_positive_number(minimum_stock):
        errors.append("Minimum stock must be a positive number.")
    
    return errors
