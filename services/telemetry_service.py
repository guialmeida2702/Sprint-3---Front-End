"""
Serviço de telemetria.

Responsável por:
 1) gerar/obter os dados brutos e convertidos dos sensores;
 2) manter o histórico em memória (st.session_state), simulando um banco
    de série temporal já "carregado";
 3) simular a chegada de uma nova leitura ("tick") — hoje via gerador
    aleatório, futuramente substituível por uma chamada real ao broker
    de IoT / API do modelo preditivo, mantendo a mesma assinatura de
    funções (mesmo contrato para o Front-end).
"""
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

from core.config import SENSOR_DEFS, STATUS_ORDER, classify_value

HISTORY_POINTS = 144   # 12h de histórico, 1 ponto a cada 5 min
FREQ_MINUTES = 5


def _raw_to_eng(raw, sensor_key: str):
    """Converte sinal bruto (ADC 0-4095) para unidade de engenharia."""
    d = SENSOR_DEFS[sensor_key]
    raw = np.clip(raw, d["raw_min"], d["raw_max"])
    frac = (raw - d["raw_min"]) / (d["raw_max"] - d["raw_min"])
    return d["eng_min"] + frac * (d["eng_max"] - d["eng_min"])


def _eng_to_raw(value, sensor_key: str):
    """Converte unidade de engenharia de volta para sinal bruto (para
    simular o dado como ele chegaria do sensor)."""
    d = SENSOR_DEFS[sensor_key]
    frac = (value - d["eng_min"]) / (d["eng_max"] - d["eng_min"])
    frac = np.clip(frac, 0, 1)
    return d["raw_min"] + frac * (d["raw_max"] - d["raw_min"])


def _baseline(sensor_key: str) -> float:
    lo, hi = sorted(SENSOR_DEFS[sensor_key]["faixa_saudavel"])
    return (lo + hi) / 2


def _generate_series(sensor_key: str, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    base = _baseline(sensor_key)
    span = SENSOR_DEFS[sensor_key]["eng_max"] - SENSOR_DEFS[sensor_key]["eng_min"]
    noise_scale = span * 0.015
    now = datetime.now()
    timestamps = [
        now - timedelta(minutes=FREQ_MINUTES * (HISTORY_POINTS - i))
        for i in range(HISTORY_POINTS)
    ]
    walk = np.cumsum(rng.normal(0, noise_scale, HISTORY_POINTS))
    walk = walk - walk.mean()
    values = base + walk * 0.3 + rng.normal(0, noise_scale * 0.5, HISTORY_POINTS)
    values = np.clip(values, SENSOR_DEFS[sensor_key]["eng_min"], SENSOR_DEFS[sensor_key]["eng_max"])
    raw = _eng_to_raw(values, sensor_key)
    return pd.DataFrame({"timestamp": timestamps, "raw": raw.astype(int), "valor": values})


def _store() -> dict:
    if "telemetry_store" not in st.session_state:
        st.session_state.telemetry_store = {}
    return st.session_state.telemetry_store


def get_series(tag: str) -> dict:
    """Retorna {sensor_key: DataFrame} para o equipamento, gerando o
    histórico sintético na primeira chamada (cache em session_state, ou
    seja, persiste durante a sessão do operador)."""
    store = _store()
    if tag not in store:
        seed = abs(hash(tag)) % (2**32)
        store[tag] = {
            sensor_key: _generate_series(sensor_key, seed + i)
            for i, sensor_key in enumerate(SENSOR_DEFS)
        }
    return store[tag]


def tick(tag: str, force_anomaly: bool = False) -> dict:
    """Simula a chegada de uma nova leitura para todos os sensores do
    equipamento informado. Usado pelo botão/timer de atualização do
    Painel de Alertas (Sprint 3) e do Dashboard (Sprint 2)."""
    series = get_series(tag)
    rng = np.random.default_rng()
    for sensor_key, df in series.items():
        last_val = df["valor"].iloc[-1]
        span = SENSOR_DEFS[sensor_key]["eng_max"] - SENSOR_DEFS[sensor_key]["eng_min"]
        step = rng.normal(0, span * 0.02)
        anomaly_chance = 1.0 if force_anomaly else 0.12
        if rng.random() < anomaly_chance:
            direction = rng.choice([-1, 1])
            step += direction * span * rng.uniform(0.15, 0.35)
        new_val = float(np.clip(last_val + step,
                                 SENSOR_DEFS[sensor_key]["eng_min"],
                                 SENSOR_DEFS[sensor_key]["eng_max"]))
        new_row = pd.DataFrame({
            "timestamp": [datetime.now()],
            "raw": [int(_eng_to_raw(new_val, sensor_key))],
            "valor": [new_val],
        })
        series[sensor_key] = pd.concat([df, new_row], ignore_index=True).tail(HISTORY_POINTS + 50)
    return latest_readings(tag)


def latest_readings(tag: str) -> dict:
    """Retorna a leitura mais recente de cada sensor, já convertida e
    classificada (Saudável / Atenção / Crítico)."""
    series = get_series(tag)
    out = {}
    for sensor_key, df in series.items():
        last = df.iloc[-1]
        out[sensor_key] = {
            "raw": int(last["raw"]),
            "valor": round(float(last["valor"]), 2),
            "unit": SENSOR_DEFS[sensor_key]["unit"],
            "status": classify_value(sensor_key, last["valor"]),
            "timestamp": last["timestamp"],
        }
    return out


def equipment_overall_status(tag: str) -> str:
    """Estado geral do ativo = pior status entre todos os sensores."""
    readings = latest_readings(tag)
    statuses = [r["status"] for r in readings.values()]
    if not statuses:
        return "Saudável"
    return min(statuses, key=lambda s: STATUS_ORDER[s])
