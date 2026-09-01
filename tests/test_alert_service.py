"""Testes de services/alert_service.py — monta os alertas prontos para
tela a partir da telemetria (Sprint 3)."""
from core.config import STATUS_ORDER, STATUS_SAUDAVEL
from core.models import Equipment
from services import alert_service, telemetry_service


def _equipment(tag):
    return Equipment(
        tag=tag, modelo="M", fabricante="F", potencia_kw=10,
        tensao_nominal_v=380, planta="Planta São Paulo", area="Área de Bombas",
    )


def test_build_alerts_empty_list_for_no_equipments():
    assert alert_service.build_alerts([]) == []


def test_build_alerts_empty_when_all_equipments_healthy(monkeypatch):
    eq = _equipment("MOT-SAUDAVEL")
    monkeypatch.setattr(
        telemetry_service, "latest_readings",
        lambda tag: {"temperatura": {
            "raw": 1000, "valor": 30.0, "unit": "°C",
            "status": STATUS_SAUDAVEL, "timestamp": None,
        }},
    )
    assert alert_service.build_alerts([eq]) == []


def test_build_alerts_generates_alert_with_summary_and_recommendation():
    eq = _equipment("MOT-ALERTA")
    status = telemetry_service.equipment_overall_status(eq.tag)
    for _ in range(6):
        if status != STATUS_SAUDAVEL:
            break
        telemetry_service.tick(eq.tag, force_anomaly=True)
        status = telemetry_service.equipment_overall_status(eq.tag)

    alerts = alert_service.build_alerts([eq])
    assert len(alerts) >= 1
    for alert in alerts:
        assert alert.tag == eq.tag
        assert alert.resumo, "resumo (NLP) não pode ser vazio"
        assert alert.recomendacao, "recomendação não pode ser vazia"
        assert alert.status in STATUS_ORDER


def test_build_alerts_are_sorted_by_severity_then_time():
    eq = _equipment("MOT-ORDENACAO")
    for _ in range(8):
        telemetry_service.tick(eq.tag, force_anomaly=True)

    alerts = alert_service.build_alerts([eq])
    severities = [STATUS_ORDER[a.status] for a in alerts]
    assert severities == sorted(severities)


def test_build_alerts_covers_multiple_equipments():
    eq1 = _equipment("MOT-M1")
    eq2 = _equipment("MOT-M2")
    for tag in (eq1.tag, eq2.tag):
        for _ in range(6):
            telemetry_service.tick(tag, force_anomaly=True)

    alerts = alert_service.build_alerts([eq1, eq2])
    tags_presentes = {a.tag for a in alerts}
    assert tags_presentes.issubset({eq1.tag, eq2.tag})
    assert len(tags_presentes) >= 1
