"""Testes de services/equipment_service.py — usa a fixture `isolated_repo`
(ver tests/conftest.py) para nunca tocar no arquivo real do projeto."""
from core.models import Equipment
from services import equipment_service


def _equipment(tag, modelo="M", fabricante="F", planta="Planta São Paulo",
               area="Área de Bombas"):
    return Equipment(
        tag=tag, modelo=modelo, fabricante=fabricante, potencia_kw=10,
        tensao_nominal_v=380, planta=planta, area=area,
    )


def test_register_and_list_equipments(isolated_repo):
    equipment_service.register_equipment(_equipment("E1"))
    assert [e.tag for e in equipment_service.list_equipments()] == ["E1"]


def test_tag_exists(isolated_repo):
    equipment_service.register_equipment(_equipment("E1"))
    assert equipment_service.tag_exists("E1")
    assert not equipment_service.tag_exists("E-NAO-CADASTRADO")


def test_get_equipment_returns_none_when_missing(isolated_repo):
    assert equipment_service.get_equipment("NAO-EXISTE") is None


def test_update_equipment(isolated_repo):
    equipment_service.register_equipment(_equipment("E2", modelo="Antigo"))
    eq = equipment_service.get_equipment("E2")
    eq.modelo = "Atualizado"
    equipment_service.update_equipment(eq)
    assert equipment_service.get_equipment("E2").modelo == "Atualizado"


def test_filter_equipments_by_planta(isolated_repo):
    equipment_service.register_equipment(_equipment("A1", planta="Planta São Paulo"))
    equipment_service.register_equipment(_equipment("A2", planta="Planta Betim"))

    resultado = equipment_service.filter_equipments(planta="Planta Betim")
    assert [e.tag for e in resultado] == ["A2"]


def test_filter_equipments_planta_todas_nao_filtra(isolated_repo):
    equipment_service.register_equipment(_equipment("A1", planta="Planta São Paulo"))
    equipment_service.register_equipment(_equipment("A2", planta="Planta Betim"))

    resultado = equipment_service.filter_equipments(planta="Todas")
    assert len(resultado) == 2


def test_filter_equipments_by_texto_busca_tag_modelo_fabricante(isolated_repo):
    equipment_service.register_equipment(_equipment("MOT-777", modelo="Alpha", fabricante="WEG"))
    equipment_service.register_equipment(_equipment("MOT-888", modelo="Beta", fabricante="ABB"))

    assert [e.tag for e in equipment_service.filter_equipments(texto="777")] == ["MOT-777"]
    assert [e.tag for e in equipment_service.filter_equipments(texto="beta")] == ["MOT-888"]
    assert [e.tag for e in equipment_service.filter_equipments(texto="weg")] == ["MOT-777"]
    assert equipment_service.filter_equipments(texto="inexistente") == []


def test_filter_equipments_combined_filters(isolated_repo):
    equipment_service.register_equipment(
        _equipment("A1", planta="Planta São Paulo", area="Área de Bombas")
    )
    equipment_service.register_equipment(
        _equipment("A2", planta="Planta São Paulo", area="Utilidades")
    )

    resultado = equipment_service.filter_equipments(
        planta="Planta São Paulo", area="Utilidades"
    )
    assert [e.tag for e in resultado] == ["A2"]
