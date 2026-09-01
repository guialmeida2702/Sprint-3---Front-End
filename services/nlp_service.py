"""
Serviço de resumos em linguagem natural (NLP).

Nesta etapa do projeto o time de NLP ainda não entregou o modelo, então
os textos abaixo são gerados por templates locais ("fake NLP"), conforme
previsto no enunciado da Sprint 3. A assinatura das funções já está
pronta para receber, no lugar do texto gerado localmente, a resposta de
um serviço real (ex.: chamada a uma API interna `/nlp/summarize`) — basta
passar o parâmetro `external_summary` / `external_recommendation` ou
trocar o corpo da função, sem alterar nenhuma tela.
"""
import random

from core.config import STATUS_CRITICO

_TEMPLATES_CRITICO = [
    "O sensor de {sensor} do equipamento {tag} registrou {valor}{unit}, "
    "ultrapassando o limite crítico. O padrão observado nas últimas "
    "leituras sugere um desvio consistente, e não uma oscilação pontual, "
    "o que reforça a necessidade de inspeção imediata.",
    "Leitura crítica identificada em {tag}: {sensor} em {valor}{unit}. "
    "O comportamento é compatível com falha iminente do componente "
    "monitorado, exigindo atenção prioritária da equipe de manutenção.",
]

_TEMPLATES_ATENCAO = [
    "O {sensor} de {tag} está em {valor}{unit}, acima da faixa "
    "considerada saudável. Ainda não é uma condição crítica, mas o "
    "histórico recente mostra tendência de leve elevação.",
    "Foi identificado um desvio moderado no sensor de {sensor} do "
    "equipamento {tag} ({valor}{unit}). Recomenda-se acompanhamento nas "
    "próximas leituras para confirmar se a tendência se mantém.",
]

_RECOMENDACOES_CRITICO = [
    "Abrir ordem de manutenção corretiva e inspecionar o ativo antes da "
    "próxima partida.",
    "Reduzir a carga do equipamento e agendar parada para inspeção nas "
    "próximas horas.",
]

_RECOMENDACOES_ATENCAO = [
    "Programar inspeção preventiva na próxima janela de manutenção "
    "disponível.",
    "Aumentar a frequência de monitoramento deste sensor nas próximas "
    "leituras.",
]


def get_summary(alert, equipment=None, external_summary: str = None) -> str:
    """Ponto único de acesso ao resumo textual do alerta.

    Se `external_summary` for informado (resposta de um serviço de NLP
    real), ele é usado diretamente; caso contrário, cai no gerador local
    (fake), determinístico por TAG+sensor para manter consistência entre
    reruns do Streamlit."""
    if external_summary:
        return external_summary
    templates = _TEMPLATES_CRITICO if alert.status == STATUS_CRITICO else _TEMPLATES_ATENCAO
    template = random.Random(alert.tag + alert.sensor_key).choice(templates)
    return template.format(
        sensor=alert.sensor_label.lower(), tag=alert.tag,
        valor=alert.valor, unit=f" {alert.unit}",
    )


def get_recommendation(alert, external_recommendation: str = None) -> str:
    """Card de apoio à decisão (Sprint 3). Mesmo princípio de seam da
    função `get_summary` acima."""
    if external_recommendation:
        return external_recommendation
    options = _RECOMENDACOES_CRITICO if alert.status == STATUS_CRITICO else _RECOMENDACOES_ATENCAO
    return random.Random(alert.tag + alert.sensor_key + "rec").choice(options)
