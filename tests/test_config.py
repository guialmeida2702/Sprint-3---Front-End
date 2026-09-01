"""Testes de core/config.py — a fonte única das regras de negócio de
classificação de status (Saudável/Atenção/Crítico), compartilhada por
todas as telas e serviços."""
from core.config import (
    SENSOR_DEFS,
    STATUS_ATENCAO,
    STATUS_CRITICO,
    STATUS_SAUDAVEL,
    classify_value,
)


def test_classify_value_saudavel_temperatura():
    assert classify_value("temperatura", 25) == STATUS_SAUDAVEL


def test_classify_value_atencao_temperatura():
    assert classify_value("temperatura", 80) == STATUS_ATENCAO


def test_classify_value_critico_temperatura():
    assert classify_value("temperatura", 130) == STATUS_CRITICO


def test_classify_value_boundary_prefers_saudavel():
    # 70°C é o limite exato entre saudável e atenção: o comportamento
    # documentado é que a faixa saudável "ganha" no empate, pois é
    # verificada primeiro em classify_value().
    assert classify_value("temperatura", 70) == STATUS_SAUDAVEL


def test_classify_value_reversed_bands_tensao():
    # Para tensão, o pior estado é ter valor BAIXO (queda de tensão),
    # ao contrário de temperatura/vibração/corrente. classify_value()
    # deve lidar com faixas "invertidas" corretamente.
    assert classify_value("tensao", 385) == STATUS_SAUDAVEL
    assert classify_value("tensao", 360) == STATUS_ATENCAO
    assert classify_value("tensao", 320) == STATUS_CRITICO


def test_classify_value_reversed_bands_rpm():
    assert classify_value("rpm", 1750) == STATUS_SAUDAVEL
    assert classify_value("rpm", 1650) == STATUS_ATENCAO
    assert classify_value("rpm", 1000) == STATUS_CRITICO


def test_all_sensor_defs_have_required_keys():
    required_keys = {
        "label", "unit", "raw_min", "raw_max", "eng_min", "eng_max",
        "faixa_saudavel", "faixa_atencao", "faixa_critica",
    }
    for sensor_key, definition in SENSOR_DEFS.items():
        missing = required_keys - definition.keys()
        assert not missing, f"Sensor '{sensor_key}' sem as chaves: {missing}"


def test_all_sensor_defs_eng_range_is_consistent():
    for sensor_key, d in SENSOR_DEFS.items():
        assert d["eng_min"] < d["eng_max"], f"Faixa de engenharia inválida em '{sensor_key}'"
        assert d["raw_min"] < d["raw_max"], f"Faixa bruta inválida em '{sensor_key}'"
