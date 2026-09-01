"""
Serviço de alertas.

Consome as leituras mais recentes de cada equipamento (via
`telemetry_service`) e monta uma lista de alertas "prontos para tela",
já contendo severidade, valor, sensor e o resumo em linguagem natural
(via `nlp_service`). Mantido isolado do processamento do modelo,
conforme exigido na Sprint 3 (arquitetura desacoplada).
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from core.config import SENSOR_DEFS, STATUS_ATENCAO, STATUS_CRITICO, STATUS_ORDER
from services import telemetry_service, nlp_service


@dataclass
class Alert:
    tag: str
    equipamento: str
    sensor_key: str
    sensor_label: str
    valor: float
    unit: str
    status: str
    timestamp: datetime
    resumo: str = ""
    recomendacao: str = ""


def build_alerts(equipments) -> List[Alert]:
    """Gera a lista de alertas ativos (Atenção/Crítico) para os
    equipamentos informados, ordenada por severidade (crítico primeiro)
    e depois por horário."""
    alerts: List[Alert] = []
    for eq in equipments:
        readings = telemetry_service.latest_readings(eq.tag)
        for sensor_key, r in readings.items():
            if r["status"] in (STATUS_ATENCAO, STATUS_CRITICO):
                alert = Alert(
                    tag=eq.tag,
                    equipamento=f"{eq.modelo} ({eq.fabricante})",
                    sensor_key=sensor_key,
                    sensor_label=SENSOR_DEFS[sensor_key]["label"],
                    valor=r["valor"],
                    unit=r["unit"],
                    status=r["status"],
                    timestamp=r["timestamp"],
                )
                alert.resumo = nlp_service.get_summary(alert, eq)
                alert.recomendacao = nlp_service.get_recommendation(alert)
                alerts.append(alert)

    alerts.sort(key=lambda a: (STATUS_ORDER[a.status], a.timestamp))
    return alerts
