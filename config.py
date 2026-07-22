import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "sims.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Ensure directories exist
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

APP_NAME = "SIMS - Stock & Inventory Management System"
PAGE_ICON = "📦"
THEME_COLOR = "#4F46E5" # Indigo

ROLES = ["Admin", "Store Manager", "Sales Staff"]
