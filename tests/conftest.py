"""
Fixtures compartilhadas pela suíte de testes.

Duas preocupações centrais:

1. `telemetry_service` usa `st.session_state` como cache de sessão. Fora do
   runtime real do Streamlit não existe um `ScriptRunContext` ativo, então
   substituímos `st.session_state` por um dicionário simples com acesso via
   atributo (o suficiente para o código de produção funcionar em testes).

2. `services.equipment_service` guarda uma instância única de
   `EquipmentRepository` apontando para o arquivo de dados "de verdade"
   (`data/storage/equipment.json`). A fixture `isolated_repo` troca essa
   instância por um repositório apontando para um arquivo temporário,
   garantindo que os testes nunca leiam/escrevam no arquivo real do
   projeto e fiquem isolados entre si.
"""
import pytest
import streamlit as st


class _FakeSessionState(dict):
    """Réplica mínima de `st.session_state` (dict + acesso por atributo)."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


@pytest.fixture(autouse=True)
def fake_session_state(monkeypatch):
    """Aplicado automaticamente em todos os testes: garante um
    `st.session_state` limpo e isolado a cada teste."""
    monkeypatch.setattr(st, "session_state", _FakeSessionState(), raising=False)
    yield


@pytest.fixture
def isolated_repo(tmp_path, monkeypatch):
    """Redireciona `services.equipment_service` para um repositório JSON
    temporário, isolado do arquivo real do projeto."""
    from data.repository import EquipmentRepository
    from services import equipment_service

    repo = EquipmentRepository(path=str(tmp_path / "equipment.json"))
    monkeypatch.setattr(equipment_service, "_repo", repo)
    return repo
