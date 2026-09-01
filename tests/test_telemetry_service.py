"""Testes de services/telemetry_service.py — geração/conversão de sinais
e simulação de novas leituras (usado pelas Sprints 1, 2 e 3)."""
from core.config import SENSOR_DEFS, STATUS_ORDER, STATUS_SAUDAVEL
from services import telemetry_service


def test_get_series_returns_all_sensors_with_full_history():
    series = telemetry_service.get_series("MOT-TESTE-SERIES")
    assert set(series.keys()) == set(SENSOR_DEFS.keys())
    for sensor_key, df in series.items():
        assert len(df) == telemetry_service.HISTORY_POINTS
        assert list(df.columns) == ["timestamp", "raw", "valor"]


def test_get_series_is_cached_in_session_state():
    first_call = telemetry_service.get_series("MOT-CACHE")
    second_call = telemetry_service.get_series("MOT-CACHE")
    assert first_call is second_call  # mesmo objeto: não regenera a cada chamada


def test_get_series_is_independent_per_tag():
    series_a = telemetry_service.get_series("MOT-A")
    series_b = telemetry_service.get_series("MOT-B")
    assert series_a is not series_b


def test_latest_readings_has_valid_status_and_types():
    readings = telemetry_service.latest_readings("MOT-READ")
    assert set(readings.keys()) == set(SENSOR_DEFS.keys())
    for sensor_key, r in readings.items():
        assert r["status"] in STATUS_ORDER
        assert isinstance(r["valor"], float)
        assert isinstance(r["raw"], int)
        assert r["unit"] == SENSOR_DEFS[sensor_key]["unit"]


def test_latest_readings_values_stay_within_engineering_range():
    readings = telemetry_service.latest_readings("MOT-RANGE")
    for sensor_key, r in readings.items():
        d = SENSOR_DEFS[sensor_key]
        assert d["eng_min"] <= r["valor"] <= d["eng_max"]


def test_tick_appends_a_new_point_to_the_history():
    tag = "MOT-TICK"
    before_len = len(telemetry_service.get_series(tag)["temperatura"])
    telemetry_service.tick(tag)
    after_len = len(telemetry_service.get_series(tag)["temperatura"])
    assert after_len == before_len + 1


def test_tick_returns_the_latest_readings():
    tag = "MOT-TICK-RETORNO"
    result = telemetry_service.tick(tag)
    assert set(result.keys()) == set(SENSOR_DEFS.keys())


def test_equipment_overall_status_is_the_worst_among_sensors():
    tag = "MOT-PIOR-CASO"
    # Força anomalias repetidas até ter certeza de que ao menos um
    # sensor saiu da faixa saudável (evita teste probabilístico frágil).
    status = telemetry_service.equipment_overall_status(tag)
    for _ in range(6):
        if status != STATUS_SAUDAVEL:
            break
        telemetry_service.tick(tag, force_anomaly=True)
        status = telemetry_service.equipment_overall_status(tag)

    readings = telemetry_service.latest_readings(tag)
    statuses = [r["status"] for r in readings.values()]
    expected = min(statuses, key=lambda s: STATUS_ORDER[s])
    assert status == expected
    assert status != STATUS_SAUDAVEL


def test_equipment_overall_status_defaults_to_saudavel_when_no_readings(monkeypatch):
    monkeypatch.setattr(telemetry_service, "latest_readings", lambda tag: {})
    assert telemetry_service.equipment_overall_status("MOT-VAZIO") == STATUS_SAUDAVEL
