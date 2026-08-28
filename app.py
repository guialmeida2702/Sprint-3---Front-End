"""
MotorWatch — Monitoramento de Motores Industriais
TCC de IA — Front-end (Sprints 1, 2 e 3)

Ponto de entrada da aplicação Streamlit. Responsável apenas por
roteamento e montagem do menu lateral — toda a lógica de negócio vive
nas camadas `core/`, `data/` e `services/`, e cada tela vive isolada em
`views/`, o que permite evoluir/trocar o front-end (ex.: migrar de
Streamlit para outro framework) sem tocar no restante do projeto.
"""
import streamlit as st

from data.seed import seed_if_empty
from views import equipment_detail, equipment_list, equipment_register, home_alerts

st.set_page_config(
    page_title="MotorWatch — Monitoramento de Motores Industriais",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

seed_if_empty()

if "page" not in st.session_state:
    st.session_state.page = "HOME"
if "selected_tag" not in st.session_state:
    st.session_state.selected_tag = None

# Registro de páginas: label exibido no menu + módulo responsável pelo
# render(). "DETAIL" fica fora da navegação principal pois é alcançada
# a partir de um clique (na lista ou em um alerta), não pelo menu.
PAGES = {
    "HOME": ("🔔 Painel de Alertas", home_alerts),
    "LIST": ("📋 Consulta de Equipamentos", equipment_list),
    "REGISTER": ("➕ Novo Cadastro", equipment_register),
    "DETAIL": ("🔍 Detalhe do Equipamento", equipment_detail),
}

with st.sidebar:
    st.markdown("## ⚙️ MotorWatch")
    st.caption("Monitoramento inteligente de motores industriais")
    st.divider()

    nav_options = ["HOME", "LIST", "REGISTER"]
    nav_labels = [PAGES[k][0] for k in nav_options]
    label_to_key = dict(zip(nav_labels, nav_options))
    key_to_label = dict(zip(nav_options, nav_labels))

    def _handle_nav_change() -> None:
        st.session_state.page = label_to_key[st.session_state["nav_radio_widget"]]

    # IMPORTANTE: um widget st.radio guarda seu próprio valor entre
    # reruns (o parâmetro `index` só vale na primeira criação do
    # widget). Se comparássemos a escolha do rádio diretamente contra
    # `st.session_state.page` a cada rerun, qualquer navegação para uma
    # página fora do menu — como "DETAIL", alcançada ao clicar em uma
    # linha da tabela ou em um card de alerta — seria imediatamente
    # revertida de volta ao menu, pois o rádio continuaria "lembrando"
    # da última opção clicada nele.
    #
    # Por isso `st.session_state.page` é a única fonte de verdade: só
    # empurramos o valor para o widget quando a página atual é uma das
    # opções do menu (ex.: ao clicar em "← Voltar para consulta"), e só
    # deixamos o próprio clique no menu (via on_change) alterar a
    # página — nunca o contrário.
    if st.session_state.page in nav_options:
        st.session_state["nav_radio_widget"] = key_to_label[st.session_state.page]

    st.radio(
        "Menu", nav_labels,
        key="nav_radio_widget",
        label_visibility="collapsed",
        on_change=_handle_nav_change,
    )

    st.divider()
    if st.session_state.selected_tag:
        st.caption(f"Equipamento em foco: **{st.session_state.selected_tag}**")
    st.caption("MotorWatch v1.0 · Sprints 1, 2 e 3 · TCC IA")

_, view_module = PAGES[st.session_state.page]
view_module.render()
