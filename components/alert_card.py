"""Componente reutilizável de card de alerta — usado tanto no Painel de
Alertas (Sprint 3) quanto no Histórico de Alertas do equipamento
(evitando duplicação de UI, conforme pedido de componentização)."""
import streamlit as st

from core.config import STATUS_COLORS, STATUS_BG_COLORS


def render_alert_card(alert, key_suffix: str = "") -> None:
    color = STATUS_COLORS.get(alert.status, "#555")
    bg = STATUS_BG_COLORS.get(alert.status, "#f5f5f5")

    with st.container(border=True):
        st.markdown(
            f"""<div style="border-left:6px solid {color};background:{bg};
            padding:10px 14px;border-radius:6px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-weight:700;color:{color};">{alert.status.upper()}</span>
                <span style="font-size:0.8rem;color:#555;">{alert.timestamp.strftime('%d/%m %H:%M')}</span>
            </div>
            <div style="font-weight:600;margin-top:4px;">{alert.tag} · {alert.equipamento}</div>
            <div style="margin-top:6px;">{alert.resumo}</div>
            <div style="margin-top:8px;font-size:0.85rem;"><b>Ação recomendada:</b> {alert.recomendacao}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button(
            "Ver equipamento →",
            key=f"btn_alert_{alert.tag}_{alert.sensor_key}{key_suffix}",
        ):
            st.session_state.page = "DETAIL"
            st.session_state.selected_tag = alert.tag
            st.rerun()
