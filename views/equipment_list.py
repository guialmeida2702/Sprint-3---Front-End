"""
Sprint 1 — Tela inicial de consulta.
Sprint 2 — Navegação por Planta/Área.

Lista os equipamentos cadastrados, com filtros por planta/área e busca
livre. Clicar em uma linha abre a ficha técnica / dashboard do ativo.
"""
import pandas as pd
import streamlit as st

from components.status_badge import status_badge_html
from core.config import PLANTAS
from services import equipment_service, telemetry_service


def render():
    st.title("📋 Consulta de Equipamentos")
    st.caption("Lista de ativos cadastrados. Clique em um equipamento para abrir a ficha técnica e o dashboard.")

    col_a, col_b, col_c = st.columns([2, 2, 3])
    with col_a:
        planta_f = st.selectbox("Planta", ["Todas"] + list(PLANTAS.keys()))
    with col_b:
        if planta_f != "Todas":
            areas = ["Todas"] + PLANTAS[planta_f]
        else:
            areas = ["Todas"] + sorted({a for lst in PLANTAS.values() for a in lst})
        area_f = st.selectbox("Área", areas)
    with col_c:
        texto_f = st.text_input("Buscar por TAG, modelo ou fabricante", "")

    if st.button("➕ Novo Cadastro"):
        st.session_state.page = "REGISTER"
        st.rerun()

    equipments = equipment_service.filter_equipments(planta_f, area_f, texto_f)

    if not equipments:
        st.info("Nenhum equipamento encontrado com os filtros atuais.")
        return

    rows = []
    for eq in equipments:
        status = telemetry_service.equipment_overall_status(eq.tag)
        rows.append({
            "TAG": eq.tag,
            "Modelo": eq.modelo,
            "Fabricante": eq.fabricante,
            "Potência (kW)": eq.potencia_kw,
            "Planta": eq.planta,
            "Área": eq.area,
            "Status": status,
        })
    df = pd.DataFrame(rows)

    st.markdown("##### Legenda de status")
    st.write(
        " &nbsp;&nbsp; ".join(status_badge_html(s) for s in ["Saudável", "Atenção", "Crítico"]),
        unsafe_allow_html=True,
    )
    st.write("")

    event = st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="equipment_table",
    )

    selected_rows = []
    if event and getattr(event, "selection", None):
        selected_rows = event.selection.get("rows", [])

    if selected_rows:
        idx = selected_rows[0]
        tag_sel = df.iloc[idx]["TAG"]
        st.session_state.page = "DETAIL"
        st.session_state.selected_tag = tag_sel
        st.rerun()

    st.caption("💡 Dica: clique em uma linha da tabela para abrir os detalhes do equipamento.")
