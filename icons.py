"""
SIMS Custom Icon Library
All icons are SVG strings designed for SIMS branding.
Use get_icon(name, size, color) to retrieve any icon.
"""

# ─────────────────────────────────────────────────────────────
#  RAW SVG DEFINITIONS
# ─────────────────────────────────────────────────────────────

_ICONS = {

    "dashboard": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="3" y="3" width="8" height="8" rx="2" fill="currentColor" opacity="0.9"/>
  <rect x="13" y="3" width="8" height="8" rx="2" fill="currentColor" opacity="0.5"/>
  <rect x="3" y="13" width="8" height="8" rx="2" fill="currentColor" opacity="0.5"/>
  <rect x="13" y="13" width="8" height="8" rx="2" fill="currentColor" opacity="0.9"/>
</svg>""",

    "pos": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="4" width="20" height="16" rx="3" stroke="currentColor" stroke-width="1.8"/>
  <path d="M7 10h2M12 10h2M17 10h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <path d="M7 14h2M12 14h2M17 14h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <path d="M2 8h20" stroke="currentColor" stroke-width="1.8"/>
</svg>""",

    "products": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <polyline points="3.27 6.96 12 12.01 20.73 6.96" stroke="currentColor" stroke-width="1.8"/>
  <line x1="12" y1="22.08" x2="12" y2="12" stroke="currentColor" stroke-width="1.8"/>
</svg>""",

    "stock": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 6h16M4 10h16M4 14h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
  <circle cx="18" cy="17" r="3" stroke="currentColor" stroke-width="1.8"/>
  <path d="M18 15.5v1.5l1 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
</svg>""",

    "users": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
  <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="1.8"/>
  <path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",

    "transactions": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="5" width="20" height="14" rx="2" stroke="currentColor" stroke-width="1.8"/>
  <path d="M2 10h20" stroke="currentColor" stroke-width="1.8"/>
  <path d="M6 15h4M14 15h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>""",

    "reports": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M18 20V10M12 20V4M6 20v-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M2 20h20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",

    "audit": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    "profile": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.8"/>
  <path d="M4 20c0-4 3.58-7 8-7s8 3 8 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",

    "logout": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
  <polyline points="16 17 21 12 16 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",

    "sun": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="1.8"/>
  <path d="M12 2v2M12 20v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M2 12h2M20 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",

    "moon": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
</svg>""",

    "bell": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",

    "search": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="1.8"/>
  <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",

    "menu": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 12h18M3 6h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>""",

    "trending_up": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <polyline points="17 6 23 6 23 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    "alert_triangle": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <line x1="12" y1="9" x2="12" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <line x1="12" y1="17" x2="12.01" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>""",

    "database": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="12" cy="5" rx="9" ry="3" stroke="currentColor" stroke-width="1.8"/>
  <path d="M21 12c0 1.66-4.03 3-9 3S3 13.66 3 12" stroke="currentColor" stroke-width="1.8"/>
  <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5" stroke="currentColor" stroke-width="1.8"/>
</svg>""",

    "box": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <polyline points="21 8 21 21 3 21 3 8" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <rect x="1" y="3" width="22" height="5" rx="1" stroke="currentColor" stroke-width="1.8"/>
  <line x1="10" y1="12" x2="14" y2="12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",

    "currency": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8"/>
  <path d="M12 8v8M9 10.5c0-1.38 1.34-2.5 3-2.5s3 1.12 3 2.5c0 1.5-1.5 2-3 2.5-1.5.5-3 1-3 2.5 0 1.38 1.34 2.5 3 2.5s3-1.12 3-2.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",

    "activity": """
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",

    "sims_logo": """
<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="4" y="4" width="40" height="40" rx="12" fill="url(#logo_grad)"/>
  <defs>
    <linearGradient id="logo_grad" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#6366f1"/>
      <stop offset="100%" stop-color="#8b5cf6"/>
    </linearGradient>
  </defs>
  <path d="M15 28c0 2.21 1.79 4 4 4h10c2.21 0 4-1.79 4-4s-1.79-4-4-4h-6c-1.66 0-3-1.34-3-3s1.34-3 3-3h10" stroke="white" stroke-width="2.2" stroke-linecap="round"/>
  <circle cx="34" cy="32" r="2" fill="white"/>
  <circle cx="14" cy="20" r="2" fill="white"/>
</svg>""",
}


def get_icon(name: str, size: int = 20, color: str = "currentColor") -> str:
    """
    Returns an inline SVG string for the given icon name.
    
    Args:
        name:  Icon key (e.g. 'dashboard', 'pos', 'users')
        size:  Width/height in pixels
        color: CSS color string (default 'currentColor')
    
    Returns:
        HTML string with the SVG ready for embedding.
    """
    svg = _ICONS.get(name, _ICONS["box"])
    # Inject width, height, color
    styled = svg.replace(
        "<svg ", 
        f'<svg width="{size}" height="{size}" style="color:{color}; display:inline-block; vertical-align:middle;" '
    )
    return styled


def get_nav_icon(page_name: str, size: int = 18, color: str = "currentColor") -> str:
    """Maps navigation page names to their icons."""
    mapping = {
        "Dashboard":       "dashboard",
        "POS Terminal":    "pos",
        "Product Catalog": "products",
        "Stock Operations":"stock",
        "Restock Requests":"stock",
        "User Management": "users",
        "Transactions":    "transactions",
        "Reports":         "reports",
        "Audit Logs":      "audit",
        "Backup & Restore":"database",
        "My Profile":      "profile",
    }
    key = mapping.get(page_name, "box")
    return get_icon(key, size, color)


def nav_icon_html(page_name: str, active: bool = False, theme: str = "dark") -> str:
    """Returns colored nav icon HTML based on active state and theme."""
    if active:
        color = "#818cf8"  # indigo accent
    else:
        color = "#64748b" if theme == "light" else "#6b7280"
    return get_nav_icon(page_name, size=16, color=color)
