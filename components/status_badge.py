"""Componente reutilizável de badge de status (cores semânticas)."""
import streamlit as st

from core.config import STATUS_COLORS, STATUS_BG_COLORS, STATUS_ICONS


def render_status_badge(status: str, extra: str = "") -> None:
    color = STATUS_COLORS.get(status, "#555")
    bg = STATUS_BG_COLORS.get(status, "#eee")
    icon = STATUS_ICONS.get(status, "⚪")
    st.markdown(
        f"""<div style="display:inline-block;padding:4px 12px;border-radius:14px;
        background:{bg};color:{color};border:1px solid {color};font-weight:600;
        font-size:0.9rem;">{icon} {status}{(' · ' + extra) if extra else ''}</div>""",
        unsafe_allow_html=True,
    )


def status_badge_html(status: str) -> str:
    """Versão em string, para uso dentro de outras composições HTML."""
    color = STATUS_COLORS.get(status, "#555")
    bg = STATUS_BG_COLORS.get(status, "#eee")
    icon = STATUS_ICONS.get(status, "⚪")
    return (
        f'<span style="padding:2px 10px;border-radius:12px;background:{bg};'
        f'color:{color};border:1px solid {color};font-weight:600;font-size:0.8rem;">'
        f'{icon} {status}</span>'
    )
