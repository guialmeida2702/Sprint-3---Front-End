"""
Testes de integração ponta a ponta, usando `streamlit.testing.v1.AppTest`
para rodar a aplicação real (app.py) e simular interações do usuário.

Diferente dos demais arquivos em `tests/`, que testam cada camada de
forma isolada, este arquivo formaliza dois bugs reais encontrados durante
a revisão manual do projeto — para garantir que não voltem a acontecer:

1. **Navegação para o Detalhe do Equipamento sendo revertida.** O widget
   `st.radio` do menu lateral guarda seu próprio valor entre reruns; a
   lógica antiga comparava a escolha do rádio contra
   `st.session_state.page` a cada rerun e, sempre que a página atual era
   "DETAIL" (fora das opções do menu), forçava a navegação de volta —
   ou seja, clicar em um equipamento nunca abria de fato a ficha dele.

2. **Inconsistência Planta/Área no cadastro.** O selectbox de "Planta"
   ficava dentro de um `st.form`, que só reflete mudanças de widgets na
   submissão — então trocar a planta não atualizava a lista de "Área"
   a tempo, permitindo salvar uma combinação inconsistente.

Nota sobre a fixture `fake_session_state` (definida em conftest.py):
ela substitui `st.session_state` por um dicionário simples, o que é
necessário para os testes unitários de `services/telemetry_service.py`,
mas quebraria o `AppTest` (que gerencia sua própria sessão real por
execução). Por isso ela é sobrescrita por um no-op neste módulo.
"""
import json
import os

import pytest
from streamlit.testing.v1 import AppTest

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "storage", "equipment.json",
)


@pytest.fixture(autouse=True)
def fake_session_state():
    """Sobrescreve, apenas neste módulo, a fixture autouse de mesmo nome
    definida em conftest.py — aqui não queremos substituir
    `st.session_state`, pois o AppTest depende do mecanismo real."""
    yield


@pytest.fixture(autouse=True)
def reset_real_data_file():
    """Estes testes rodam a aplicação real de ponta a ponta, então usam
    o mesmo arquivo de dados (`data/storage/equipment.json`) que a
    aplicação usaria fora de testes. Resetamos para vazio antes e depois
    de cada teste: isso garante que `seed_if_empty()` sempre repovoe os
    4 equipamentos de exemplo do zero, e que nenhum dado de teste fique
    no arquivo real do projeto."""
    def _clear():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

    _clear()
    yield
    _clear()


APP_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"
)


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_FILE)
    at.run(timeout=60)
    assert not at.exception
    return at


def test_app_starts_on_home_page():
    at = _fresh_app()
    assert at.session_state["page"] == "HOME"
    assert at.title[0].value == "🔔 Painel de Alertas e Estados"


def test_menu_navigates_between_all_pages():
    at = _fresh_app()

    at.radio[0].set_value("📋 Consulta de Equipamentos").run(timeout=60)
    assert at.session_state["page"] == "LIST"
    assert not at.exception

    at.radio[0].set_value("➕ Novo Cadastro").run(timeout=60)
    assert at.session_state["page"] == "REGISTER"
    assert not at.exception

    at.radio[0].set_value("🔔 Painel de Alertas").run(timeout=60)
    assert at.session_state["page"] == "HOME"
    assert not at.exception


def test_navigating_to_detail_does_not_bounce_back_to_menu():
    """Regressão do bug de navegação (ver docstring do módulo)."""
    at = _fresh_app()

    at.session_state["page"] = "DETAIL"
    at.session_state["selected_tag"] = "MOT-001"
    at.run(timeout=60)

    assert at.session_state["page"] == "DETAIL", (
        "BUG DE REGRESSÃO: a página voltou para "
        f"'{at.session_state['page']}' em vez de permanecer em DETAIL."
    )
    assert "MOT-001" in at.title[0].value

    # Um segundo rerun (equivalente a qualquer interação subsequente
    # dentro da própria tela de detalhe) não pode causar bounce.
    at.run(timeout=60)
    assert at.session_state["page"] == "DETAIL"


def test_voltar_para_consulta_resyncs_menu_radio():
    at = _fresh_app()
    at.session_state["page"] = "DETAIL"
    at.session_state["selected_tag"] = "MOT-001"
    at.run(timeout=60)

    voltar_btn = [b for b in at.button if "Voltar para consulta" in b.label][0]
    voltar_btn.click().run(timeout=60)

    assert at.session_state["page"] == "LIST"
    assert at.radio[0].value == "📋 Consulta de Equipamentos"


def test_clicking_ver_equipamento_alert_card_reaches_detail():
    at = _fresh_app()

    atualizar_btn = [b for b in at.button if "Atualizar agora" in b.label][0]
    ver_btns = []
    for _ in range(6):
        atualizar_btn.click().run(timeout=60)
        ver_btns = [b for b in at.button if "Ver equipamento" in b.label]
        if ver_btns:
            break

    assert ver_btns, "Nenhum alerta foi gerado para testar o clique no card"
    ver_btns[0].click().run(timeout=60)
    assert at.session_state["page"] == "DETAIL"


def test_register_form_saves_consistent_planta_area_pair():
    """Regressão do bug de Planta/Área (ver docstring do módulo)."""
    at = _fresh_app()
    at.session_state["page"] = "REGISTER"
    at.run(timeout=60)

    planta_sb = at.selectbox(key="equipment_form_new_planta")
    planta_sb.select("Planta Manaus").run(timeout=60)

    area_sb = [sb for sb in at.selectbox if sb.label == "Área *"][0]
    assert area_sb.value in ("Injeção Plástica", "Área de Solda"), (
        "BUG DE REGRESSÃO: opções de Área não acompanharam a Planta escolhida."
    )

    tag_input = [ti for ti in at.text_input if ti.label == "TAG de identificação *"][0]
    modelo_input = [ti for ti in at.text_input if ti.label == "Modelo *"][0]
    fabricante_input = [ti for ti in at.text_input if ti.label == "Fabricante *"][0]

    tag_input.set_value("MOT-REGRESSAO").run(timeout=60)
    modelo_input.set_value("Modelo X").run(timeout=60)
    fabricante_input.set_value("Fabricante X").run(timeout=60)

    submit_btn = [b for b in at.button if "Salvar cadastro" in b.label][0]
    submit_btn.click().run(timeout=60)
    assert not at.exception

    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    saved = [e for e in data if e["tag"] == "MOT-REGRESSAO"][0]
    assert saved["planta"] == "Planta Manaus"
    assert saved["area"] in ("Injeção Plástica", "Área de Solda")
