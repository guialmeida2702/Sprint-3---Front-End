"""Testes de core/models.py — contrato de dados do Equipamento."""
import pytest

from core.models import Equipment


def _base_equipment(**overrides):
    defaults = dict(
        tag="X1", modelo="Modelo", fabricante="Fabricante", potencia_kw=10.0,
        tensao_nominal_v=380.0, planta="Planta São Paulo", area="Área de Bombas",
    )
    defaults.update(overrides)
    return Equipment(**defaults)


def test_equipment_generates_data_cadastro_by_default():
    eq = _base_equipment()
    assert eq.data_cadastro  # não pode ser vazio/None
    assert isinstance(eq.data_cadastro, str)


def test_equipment_default_optional_fields():
    eq = _base_equipment()
    assert eq.imagem_placa_b64 is None
    assert eq.observacoes == ""


def test_equipment_to_dict_contains_all_fields():
    eq = _base_equipment(observacoes="teste")
    d = eq.to_dict()
    assert d["tag"] == "X1"
    assert d["observacoes"] == "teste"
    assert set(d.keys()) == {
        "tag", "modelo", "fabricante", "potencia_kw", "tensao_nominal_v",
        "planta", "area", "data_cadastro", "imagem_placa_b64", "observacoes",
    }


def test_equipment_roundtrip_to_dict_from_dict():
    eq = _base_equipment(tag="X2", observacoes="ida e volta")
    restored = Equipment.from_dict(eq.to_dict())
    assert restored == eq


def test_equipment_explicit_data_cadastro_is_preserved():
    eq = Equipment(
        tag="X3", modelo="M", fabricante="F", potencia_kw=1, tensao_nominal_v=220,
        planta="P", area="A", data_cadastro="2020-01-01T00:00:00",
    )
    assert eq.data_cadastro == "2020-01-01T00:00:00"


def test_equipment_from_dict_ignores_unknown_keys():
    # Simula um arquivo de dados de uma versão futura do schema, com um
    # campo extra que ainda não existe no dataclass atual. O sistema não
    # deve quebrar ao carregar esse registro.
    d = {
        "tag": "X4", "modelo": "M", "fabricante": "F", "potencia_kw": 10.0,
        "tensao_nominal_v": 220.0, "planta": "P", "area": "A",
        "data_cadastro": "2020-01-01T00:00:00", "imagem_placa_b64": None,
        "observacoes": "",
        "campo_do_futuro_que_ainda_nao_existe": "qualquer coisa",
    }
    eq = Equipment.from_dict(d)
    assert eq.tag == "X4"
    assert not hasattr(eq, "campo_do_futuro_que_ainda_nao_existe")


def test_equipment_from_dict_still_requires_mandatory_fields():
    # Campos obrigatórios ausentes devem continuar falhando alto (não é
    # desejável mascarar um registro genuinamente corrompido).
    with pytest.raises(TypeError):
        Equipment.from_dict({"tag": "X5"})
