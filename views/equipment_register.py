"""Sprint 1 — Módulo de Cadastro Técnico."""
import streamlit as st

from components.equipment_form import render_equipment_form


def render():
    st.title("➕ Novo Cadastro de Equipamento")
    st.caption("Preencha os dados técnicos do motor. Campos com * são obrigatórios.")

    if st.button("← Voltar para consulta"):
        st.session_state.page = "LIST"
        st.rerun()

    eq = render_equipment_form()

    if eq:
        st.session_state.selected_tag = eq.tag
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ver ficha técnica do equipamento cadastrado →", width="stretch"):
                st.session_state.page = "DETAIL"
                st.rerun()
        with col2:
            if st.button("Cadastrar outro equipamento", width="stretch"):
                st.rerun()
