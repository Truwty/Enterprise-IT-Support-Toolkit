import customtkinter as ctk

# Colors are stored as (Light Mode Hex, Dark Mode Hex)
COLORS = {
    "bg_primary":       ("#F9FAFB", "#0B0F19"),    # Deep app background
    "bg_secondary":     ("#FFFFFF", "#111827"),    # Panel/Sidebar background 
    "bg_tertiary":      ("#F3F4F6", "#1F2937"),    # Card background 
    "bg_hover":         ("#E5E7EB", "#374151"),    # Hover state 

    "accent_blue":      ("#2563EB", "#3B82F6"),    # Primary action 
    "accent_green":     ("#059669", "#10B981"),    # Success 
    "accent_orange":    ("#D97706", "#F59E0B"),    # Warning 
    "accent_red":       ("#DC2626", "#EF4444"),    # Danger 
    "accent_purple":    ("#7C3AED", "#8B5CF6"),    # Special features 
    "accent_cyan":      ("#0891B2", "#06B6D4"),    # Network/Active 

    "text_primary":     ("#111827", "#F9FAFB"),    # Main text 
    "text_secondary":   ("#4B5563", "#9CA3AF"),    # Muted text 
    "text_disabled":    ("#9CA3AF", "#4B5563"),    # Disabled text 

    "border":           ("#D1D5DB", "#374151"),    # Standard border
    "border_active":    ("#2563EB", "#3B82F6"),    # Active border

    "status_online":    ("#059669", "#10B981"),
    "status_offline":   ("#DC2626", "#EF4444"),
    "status_warning":   ("#D97706", "#F59E0B"),
    "status_unknown":   ("#9CA3AF", "#9CA3AF"),

    "graph_cpu":        ("#2563EB", "#3B82F6"),
    "graph_ram":        ("#7C3AED", "#8B5CF6"),
    "graph_disk":       ("#059669", "#10B981"),
    "graph_network":    ("#0891B2", "#06B6D4"),
    "graph_bg":         ("#FFFFFF", "#111827"),    
    "graph_grid":       ("#F3F4F6", "#1F2937"),    
}

FONTS = {
    "title":        ("Segoe UI", 26, "bold"),
    "heading":      ("Segoe UI", 18, "bold"),
    "subheading":   ("Segoe UI", 14, "bold"),
    "body":         ("Segoe UI", 13),
    "small":        ("Segoe UI", 11),
    "mono":         ("Cascadia Code", 12),  
    "mono_small":   ("Cascadia Code", 10),
    "badge":        ("Segoe UI", 11, "bold"),
    "metric":       ("Segoe UI", 48, "bold"), 
}

def get_color(color_name: str) -> str:
    """
    Returns the specific hex string based on current theme mode.
    Used for components that don't natively support CTk tuples (like Matplotlib/Canvas).
    """
    mode = ctk.get_appearance_mode()
    val = COLORS.get(color_name, ("#FFFFFF", "#000000"))
    if isinstance(val, tuple):
        return val[0] if mode == "Light" else val[1]
    return val
