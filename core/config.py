"""
Configurações centrais do sistema: cores semânticas, limites operacionais
e parâmetros de sensores.

Mantido isolado (sem dependência de Streamlit) para que os times de
Front-end e Modelo (Backend/ML) compartilhem exatamente as mesmas regras
de negócio (faixas saudável/atenção/crítico) sem duplicar lógica.
"""

# --- Status operacional e cores semânticas ---------------------------------

STATUS_SAUDAVEL = "Saudável"
STATUS_ATENCAO = "Atenção"
STATUS_CRITICO = "Crítico"

STATUS_COLORS = {
    STATUS_SAUDAVEL: "#1E8449",   # verde
    STATUS_ATENCAO: "#B7950B",    # amarelo (contraste adequado)
    STATUS_CRITICO: "#B03A2E",    # vermelho
}

STATUS_BG_COLORS = {
    STATUS_SAUDAVEL: "#E9F7EF",
    STATUS_ATENCAO: "#FEF9E7",
    STATUS_CRITICO: "#FDEDEC",
}

STATUS_ICONS = {
    STATUS_SAUDAVEL: "🟢",
    STATUS_ATENCAO: "🟡",
    STATUS_CRITICO: "🔴",
}

# Usado para ordenar alertas: crítico primeiro
STATUS_ORDER = {STATUS_CRITICO: 0, STATUS_ATENCAO: 1, STATUS_SAUDAVEL: 2}

# --- Definição dos sensores monitorados -------------------------------------
# Simula um ADC de 0-4095 (sinal bruto) convertido para unidade de
# engenharia, com faixas operacionais para classificação de estado.
SENSOR_DEFS = {
    "temperatura": {
        "label": "Temperatura",
        "unit": "°C",
        "raw_min": 0, "raw_max": 4095,
        "eng_min": 0, "eng_max": 150,
        "faixa_saudavel": (0, 70),
        "faixa_atencao": (70, 90),
        "faixa_critica": (90, 150),
    },
    "vibracao": {
        "label": "Vibração",
        "unit": "mm/s",
        "raw_min": 0, "raw_max": 4095,
        "eng_min": 0, "eng_max": 20,
        "faixa_saudavel": (0, 4.5),
        "faixa_atencao": (4.5, 7.1),
        "faixa_critica": (7.1, 20),
    },
    "corrente": {
        "label": "Corrente",
        "unit": "A",
        "raw_min": 0, "raw_max": 4095,
        "eng_min": 0, "eng_max": 60,
        "faixa_saudavel": (0, 40),
        "faixa_atencao": (40, 50),
        "faixa_critica": (50, 60),
    },
    "tensao": {
        "label": "Tensão",
        "unit": "V",
        "raw_min": 0, "raw_max": 4095,
        "eng_min": 300, "eng_max": 460,
        "faixa_saudavel": (370, 400),
        "faixa_atencao": (350, 370),
        "faixa_critica": (300, 350),
    },
    "rpm": {
        "label": "Rotação",
        "unit": "RPM",
        "raw_min": 0, "raw_max": 4095,
        "eng_min": 0, "eng_max": 3600,
        "faixa_saudavel": (1700, 1810),
        "faixa_atencao": (1600, 1700),
        "faixa_critica": (0, 1600),
    },
}

# --- Estrutura de navegação por Planta/Área (Sprint 2) ----------------------
PLANTAS = {
    "Planta São Paulo": ["Área de Compressores", "Área de Bombas", "Utilidades"],
    "Planta Betim": ["Linha de Montagem", "Área de Pintura"],
    "Planta Manaus": ["Injeção Plástica", "Área de Solda"],
}

# --- Persistência local -------------------------------------------------
DATA_DIR = "data/storage"
EQUIPMENT_FILE = f"{DATA_DIR}/equipment.json"


# --- Helpers de classificação -----------------------------------------------

def _in_range(value: float, band) -> bool:
    lo, hi = sorted(band)
    return lo <= value <= hi


def classify_value(sensor_key: str, value: float) -> str:
    """Classifica uma leitura de sensor em Saudável / Atenção / Crítico
    de acordo com as faixas operacionais definidas em SENSOR_DEFS."""
    d = SENSOR_DEFS[sensor_key]
    if _in_range(value, d["faixa_saudavel"]):
        return STATUS_SAUDAVEL
    if _in_range(value, d["faixa_atencao"]):
        return STATUS_ATENCAO
    return STATUS_CRITICO
