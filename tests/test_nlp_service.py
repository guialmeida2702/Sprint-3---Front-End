"""Testes de services/nlp_service.py — geração local de resumos (fake
NLP) e o "seam" para receber o resultado de um serviço de NLP real."""
from dataclasses import dataclass

from core.config import STATUS_ATENCAO, STATUS_CRITICO
from services import nlp_service


@dataclass
class _DummyAlert:
    tag: str
    sensor_key: str
    sensor_label: str
    valor: float
    unit: str
    status: str


def test_get_summary_uses_external_summary_when_provided():
    alert = _DummyAlert("MOT-1", "temperatura", "Temperatura", 95, "°C", STATUS_CRITICO)
    resumo = nlp_service.get_summary(alert, external_summary="Resumo gerado pelo modelo real de NLP.")
    assert resumo == "Resumo gerado pelo modelo real de NLP."


def test_get_summary_fake_is_deterministic_for_same_alert():
    a1 = _DummyAlert("MOT-2", "vibracao", "Vibração", 8.1, "mm/s", STATUS_CRITICO)
    a2 = _DummyAlert("MOT-2", "vibracao", "Vibração", 8.1, "mm/s", STATUS_CRITICO)
    assert nlp_service.get_summary(a1) == nlp_service.get_summary(a2)


def test_get_summary_mentions_tag_and_sensor():
    alert = _DummyAlert("MOT-999", "vibracao", "Vibração", 8.2, "mm/s", STATUS_CRITICO)
    resumo = nlp_service.get_summary(alert)
    assert "MOT-999" in resumo
    assert "vibra" in resumo.lower()


def test_get_summary_differs_between_critico_and_atencao_templates():
    critico = _DummyAlert("MOT-3", "temperatura", "Temperatura", 100, "°C", STATUS_CRITICO)
    atencao = _DummyAlert("MOT-3", "temperatura", "Temperatura", 100, "°C", STATUS_ATENCAO)

    formatted_criticos = {
        t.format(sensor="temperatura", tag="MOT-3", valor=100, unit=" °C")
        for t in nlp_service._TEMPLATES_CRITICO
    }
    formatted_atencoes = {
        t.format(sensor="temperatura", tag="MOT-3", valor=100, unit=" °C")
        for t in nlp_service._TEMPLATES_ATENCAO
    }

    assert nlp_service.get_summary(critico) in formatted_criticos
    assert nlp_service.get_summary(atencao) in formatted_atencoes
    assert formatted_criticos.isdisjoint(formatted_atencoes)


def test_get_recommendation_uses_external_when_provided():
    alert = _DummyAlert("MOT-4", "corrente", "Corrente", 55, "A", STATUS_CRITICO)
    rec = nlp_service.get_recommendation(alert, external_recommendation="Trocar rolamento.")
    assert rec == "Trocar rolamento."


def test_get_recommendation_is_non_empty_for_both_severities():
    critico = _DummyAlert("MOT-5", "corrente", "Corrente", 55, "A", STATUS_CRITICO)
    atencao = _DummyAlert("MOT-5", "corrente", "Corrente", 45, "A", STATUS_ATENCAO)
    assert nlp_service.get_recommendation(critico)
    assert nlp_service.get_recommendation(atencao)
