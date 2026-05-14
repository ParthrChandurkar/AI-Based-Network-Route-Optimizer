"""
utils.py — Shared constants and helpers (NO streamlit imports).
"""

RISK_COLORS = {
    "Low":     "#22c55e",
    "Medium":  "#f59e0b",
    "High":    "#ef4444",
    "Unknown": "#94a3b8",
}

ALGO_COLORS = {
    "Traditional": "#3b82f6",
    "AI-Enhanced": "#10b981",
    "Failed":      "#ef4444",
    "Default":     "#475569",
}

def risk_color(label: str) -> str:
    return RISK_COLORS.get(label, RISK_COLORS["Unknown"])
