"""Componente reutilizável de formulário de cadastro/edição técnica do
equipamento (Sprint 1), com validação e feedback visual (human-in-the-loop)."""
import base64

import streamlit as st

from core.config import PLANTAS
from core.models import Equipment
from services import equipment_service


def render_equipment_form(existing: Equipment = None):
    """Renderiza o formulário. Se `existing` for informado, o formulário
    abre em modo de edição (TAG travada). Retorna o Equipment salvo, ou
    None enquanto o usuário não submeter (ou se houver erro de validação)."""
    editing = existing is not None
    form_key = f"equipment_form_{existing.tag if editing else 'new'}"

    plantas_list = list(PLANTAS.keys())
    default_planta = existing.planta if editing else plantas_list[0]

    # IMPORTANTE: este selectbox fica FORA do st.form de propósito.
    # Widgets dentro de um st.form não disparam rerun ao mudar de valor
    # (só na submissão) — então, se "Planta" estivesse dentro do form, a
    # lista de "Área" (que depende da planta escolhida) continuaria
    # mostrando as opções antigas na tela até o usuário clicar em salvar,
    # permitindo gravar uma combinação Planta/Área inconsistente (ex.:
    # Planta Betim + uma área que pertence à Planta São Paulo).
    # Colocando-o fora do form, a escolha de planta atualiza a lista de
    # área imediatamente, antes mesmo de o usuário submeter o formulário.
    planta = st.selectbox(
        "Planta *", plantas_list,
        index=plantas_list.index(default_planta),
        key=f"{form_key}_planta",
    )
    area_options = PLANTAS[planta]
    default_area_index = (
        area_options.index(existing.area)
        if editing and existing.area in area_options
        else 0
    )

    with st.form(form_key, clear_on_submit=not editing):
        col1, col2 = st.columns(2)
        with col1:
            tag = st.text_input(
                "TAG de identificação *",
                value=existing.tag if editing else "",
                disabled=editing,
                help="Identificador único do ativo, ex: MOT-005",
            )
            modelo = st.text_input("Modelo *", value=existing.modelo if editing else "")
            fabricante = st.text_input("Fabricante *", value=existing.fabricante if editing else "")
            potencia = st.number_input(
                "Potência (kW) *", min_value=0.0, step=0.5,
                value=float(existing.potencia_kw) if editing else 0.0,
            )
        with col2:
            tensao = st.number_input(
                "Tensão nominal (V) *", min_value=0.0, step=1.0,
                value=float(existing.tensao_nominal_v) if editing else 380.0,
            )
            area = st.selectbox("Área *", area_options, index=default_area_index)
            imagem = st.file_uploader(
                "Imagem da placa (simulada ou real)", type=["png", "jpg", "jpeg"],
                help="Representa a imagem que, no fluxo completo, seria lida por visão computacional.",
            )
        obs = st.text_area("Observações", value=existing.observacoes if editing else "")

        submitted = st.form_submit_button(
            "💾 Salvar cadastro" if not editing else "💾 Salvar alterações",
            width="stretch",
        )

    if not submitted:
        return None

    erros = []
    if not tag.strip():
        erros.append("TAG é obrigatória.")
    if not modelo.strip():
        erros.append("Modelo é obrigatório.")
    if not fabricante.strip():
        erros.append("Fabricante é obrigatório.")
    if not editing and equipment_service.tag_exists(tag.strip()):
        erros.append(f"Já existe um equipamento cadastrado com a TAG '{tag}'.")

    if erros:
        for e in erros:
            st.error(e, icon="🚫")
        return None

    img_b64 = existing.imagem_placa_b64 if editing else None
    if imagem is not None:
        img_b64 = base64.b64encode(imagem.read()).decode("utf-8")

    kwargs = dict(
        tag=tag.strip(), modelo=modelo.strip(), fabricante=fabricante.strip(),
        potencia_kw=potencia, tensao_nominal_v=tensao, planta=planta, area=area,
        imagem_placa_b64=img_b64, observacoes=obs,
    )
    if editing:
        kwargs["data_cadastro"] = existing.data_cadastro

    eq = Equipment(**kwargs)

    if editing:
        equipment_service.update_equipment(eq)
        st.success(f"Equipamento {eq.tag} atualizado com sucesso!", icon="✅")
    else:
        equipment_service.register_equipment(eq)
        st.success(f"Equipamento {eq.tag} cadastrado com sucesso!", icon="✅")

    return eq
