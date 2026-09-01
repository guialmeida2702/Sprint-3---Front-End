"""
Sprint 1 — Ficha técnica completa + visualização de dados brutos.
Sprint 2 — Dashboard de telemetria, gráficos temporais e imagem da placa.
Sprint 3 — Histórico de alertas do equipamento (reaproveitando o
           componente de card de alerta).
"""
import base64

import pandas as pd
import streamlit as st

from components.alert_card import render_alert_card
from components.charts import gauge_chart, time_series_chart
from components.equipment_form import render_equipment_form
from components.status_badge import render_status_badge
from core.config import SENSOR_DEFS
from services import alert_service, equipment_service, telemetry_service


def render():
    tag = st.session_state.get("selected_tag")
    eq = equipment_service.get_equipment(tag) if tag else None

    if not eq:
        st.warning("Nenhum equipamento selecionado.")
        if st.button("← Voltar para consulta"):
            st.session_state.page = "LIST"
            st.rerun()
        return

    top1, top2 = st.columns([5, 1])
    with top1:
        st.title(f"{eq.tag} — {eq.modelo}")
        st.caption(f"{eq.fabricante} · {eq.planta} · {eq.area}")
    with top2:
        if st.button("🔄 Atualizar leituras", width="stretch"):
            telemetry_service.tick(eq.tag)
            st.toast("Leituras do equipamento atualizadas.", icon="🔄")
            st.rerun()

    overall_status = telemetry_service.equipment_overall_status(eq.tag)
    render_status_badge(overall_status, extra="estado geral do ativo")

    if st.button("← Voltar para consulta"):
        st.session_state.page = "LIST"
        st.rerun()

    tab_ficha, tab_dash, tab_hist = st.tabs(
        ["📋 Ficha Técnica", "📊 Dashboard Operacional", "🕘 Histórico de Alertas"],
        key="equipment_detail_tabs",
    )

    with tab_ficha:
        _render_ficha(eq)
    with tab_dash:
        _render_dashboard(eq)
    with tab_hist:
        _render_historico(eq)


def _render_ficha(eq) -> None:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Dados cadastrais")
        st.markdown(f"""
| Campo | Valor |
|---|---|
| TAG | **{eq.tag}** |
| Modelo | {eq.modelo} |
| Fabricante | {eq.fabricante} |
| Potência | {eq.potencia_kw} kW |
| Tensão nominal | {eq.tensao_nominal_v} V |
| Planta | {eq.planta} |
| Área | {eq.area} |
| Cadastrado em | {eq.data_cadastro} |
""")
        if eq.observacoes:
            st.markdown(f"**Observações:** {eq.observacoes}")

        with st.expander("✏️ Editar cadastro"):
            render_equipment_form(existing=eq)

    with col2:
        st.subheader("Imagem da placa")
        if eq.imagem_placa_b64:
            st.image(
                base64.b64decode(eq.imagem_placa_b64),
                width="stretch",
                caption="Imagem associada ao cadastro do ativo.",
            )
        else:
            st.info(
                "Nenhuma imagem cadastrada. Este espaço está preparado para exibir a "
                "imagem da placa (real ou simulada) associada aos dados extraídos via "
                "visão computacional, quando o módulo estiver integrado.",
                icon="🖼️",
            )

    st.divider()
    st.subheader("Visualização de dados brutos")
    st.caption("Sinal bruto do sensor (contagem ADC 0–4095) convertido para unidade de engenharia.")

    readings = telemetry_service.latest_readings(eq.tag)
    raw_rows = [
        {
            "Sensor": SENSOR_DEFS[k]["label"],
            "Sinal bruto (ADC)": r["raw"],
            "Valor convertido": r["valor"],
            "Unidade": r["unit"],
            "Status": r["status"],
        }
        for k, r in readings.items()
    ]
    st.dataframe(pd.DataFrame(raw_rows), width="stretch", hide_index=True)


def _render_dashboard(eq) -> None:
    st.subheader("Telemetria em tempo real")
    readings = telemetry_service.latest_readings(eq.tag)
    series = telemetry_service.get_series(eq.tag)

    cols = st.columns(len(SENSOR_DEFS))
    for col, (sensor_key, r) in zip(cols, readings.items()):
        with col:
            st.plotly_chart(
                gauge_chart(sensor_key, r["valor"]),
                width="stretch",
                key=f"gauge_{eq.tag}_{sensor_key}",
            )

    st.divider()
    st.subheader("Séries temporais — histórico")
    sensor_options = {SENSOR_DEFS[k]["label"]: k for k in SENSOR_DEFS}
    chosen_labels = st.multiselect(
        "Sensores para exibir",
        list(sensor_options.keys()),
        default=list(sensor_options.keys())[:2],
    )
    for label in chosen_labels:
        k = sensor_options[label]
        st.plotly_chart(
            time_series_chart(series[k], k),
            width="stretch",
            key=f"ts_{eq.tag}_{k}",
        )


def _render_historico(eq) -> None:
    st.subheader("Histórico de alertas deste equipamento")
    alerts = alert_service.build_alerts([eq])
    if not alerts:
        st.success("Nenhum alerta ativo para este equipamento no momento.", icon="✅")
        return
    for a in alerts:
        render_alert_card(a, key_suffix="_hist")
