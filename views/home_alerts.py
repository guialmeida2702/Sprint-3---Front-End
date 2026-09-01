"""
Sprint 3 — Painel de Alertas e Estados.

Página inicial da aplicação (antes da seleção de equipamentos), com:
 - resumos inteligentes (NLP, hoje simulado) por alerta;
 - cards de apoio inicial à decisão (ação recomendada);
 - atualização manual (botão) e automática (timer, quando o pacote
   `streamlit-autorefresh` está instalado);
 - simulação garantida de ao menos uma notificação após atualização,
   caso nenhum alerta esteja ativo no momento.
"""
import random
from datetime import datetime

import streamlit as st

from components.alert_card import render_alert_card
from core.config import STATUS_ATENCAO, STATUS_CRITICO, STATUS_SAUDAVEL
from services import alert_service, equipment_service, telemetry_service

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False


def render():
    st.title("🔔 Painel de Alertas e Estados")
    st.caption("Visão geral do estado operacional de todos os ativos monitorados.")

    top = st.columns([1.2, 1.4, 2])
    with top[0]:
        if st.button("🔄 Atualizar agora", width="stretch"):
            _refresh_all(ensure_alert=True)
    with top[1]:
        auto = st.toggle(
            "Atualização automática (15s)",
            value=st.session_state.get("auto_refresh", False),
            help="Atualiza o painel automaticamente, simulando a chegada de novas leituras.",
        )
        st.session_state.auto_refresh = auto
    with top[2]:
        last = st.session_state.get("last_refresh")
        st.caption(f"Última atualização: {last.strftime('%d/%m/%Y %H:%M:%S') if last else '—'}")

    if st.session_state.get("auto_refresh"):
        if HAS_AUTOREFRESH:
            st_autorefresh(interval=15_000, key="alerts_autorefresh")
            _refresh_all(silent=True, ensure_alert=True)
        else:
            st.info(
                "Para habilitar o timer automático, instale a dependência opcional "
                "`streamlit-autorefresh` (já incluída no requirements.txt). "
                "Por enquanto, use o botão de atualização manual.",
                icon="ℹ️",
            )

    equipments = equipment_service.list_equipments()
    if not equipments:
        st.warning("Nenhum equipamento cadastrado ainda. Vá em **Consulta de Equipamentos → Novo Cadastro** para começar.")
        return

    statuses = {eq.tag: telemetry_service.equipment_overall_status(eq.tag) for eq in equipments}
    n_ok = sum(1 for s in statuses.values() if s == STATUS_SAUDAVEL)
    n_atn = sum(1 for s in statuses.values() if s == STATUS_ATENCAO)
    n_crit = sum(1 for s in statuses.values() if s == STATUS_CRITICO)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ativos monitorados", len(equipments))
    k2.metric("🟢 Saudáveis", n_ok)
    k3.metric("🟡 Em atenção", n_atn)
    k4.metric("🔴 Críticos", n_crit)

    st.divider()

    alerts = alert_service.build_alerts(equipments)

    if not alerts:
        st.success(
            "✅ Nenhum alerta ativo no momento. Todos os equipamentos estão dentro da "
            "faixa operacional saudável.",
            icon="✅",
        )
        return

    st.subheader(f"Alertas ativos ({len(alerts)})")
    st.caption("Ordenados por severidade — críticos primeiro.")
    for alert in alerts:
        render_alert_card(alert)


def _refresh_all(silent: bool = False, ensure_alert: bool = False) -> None:
    equipments = equipment_service.list_equipments()
    for eq in equipments:
        telemetry_service.tick(eq.tag)

    if ensure_alert and equipments:
        current_alerts = alert_service.build_alerts(equipments)
        if not current_alerts:
            target = random.choice(equipments)
            telemetry_service.tick(target.tag, force_anomaly=True)

    st.session_state.last_refresh = datetime.now()
    if not silent:
        st.toast("Painel atualizado com as leituras mais recentes.", icon="🔄")
        st.rerun()
