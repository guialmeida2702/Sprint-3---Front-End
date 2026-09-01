"""Componentes de visualização gráfica (Plotly), reutilizados no
Dashboard Operacional (Sprint 2)."""
import plotly.graph_objects as go

from core.config import SENSOR_DEFS, STATUS_COLORS, STATUS_SAUDAVEL, STATUS_ATENCAO, STATUS_CRITICO


def time_series_chart(df, sensor_key: str):
    d = SENSOR_DEFS[sensor_key]
    lo_s, hi_s = sorted(d["faixa_saudavel"])

    fig = go.Figure()
    fig.add_hrect(y0=lo_s, y1=hi_s, fillcolor=STATUS_COLORS[STATUS_SAUDAVEL],
                  opacity=0.10, line_width=0)
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["valor"], mode="lines",
        line=dict(color="#2E86C1", width=2), name=d["label"],
    ))
    fig.update_layout(
        title=f"{d['label']} ({d['unit']}) — histórico",
        margin=dict(l=10, r=10, t=40, b=10), height=280,
        xaxis_title=None, yaxis_title=d["unit"],
        plot_bgcolor="white",
    )
    return fig


def gauge_chart(sensor_key: str, value: float):
    d = SENSOR_DEFS[sensor_key]
    lo_s, hi_s = sorted(d["faixa_saudavel"])
    lo_a, hi_a = sorted(d["faixa_atencao"])
    lo_c, hi_c = sorted(d["faixa_critica"])

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": f" {d['unit']}"},
        title={"text": d["label"]},
        gauge={
            "axis": {"range": [d["eng_min"], d["eng_max"]]},
            "bar": {"color": "#2E4053"},
            "steps": [
                {"range": [lo_c, hi_c], "color": STATUS_COLORS[STATUS_CRITICO]},
                {"range": [lo_a, hi_a], "color": STATUS_COLORS[STATUS_ATENCAO]},
                {"range": [lo_s, hi_s], "color": STATUS_COLORS[STATUS_SAUDAVEL]},
            ],
        },
    ))
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=10))
    return fig
