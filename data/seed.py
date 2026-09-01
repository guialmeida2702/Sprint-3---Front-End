"""Popula o repositório com alguns equipamentos de exemplo na primeira
execução, para que a demonstração em vídeo já tenha dados para navegar."""
from core.models import Equipment
from data.repository import EquipmentRepository

SEED_EQUIPMENTS = [
    Equipment(
        tag="MOT-001", modelo="W22 IR3 Premium", fabricante="WEG",
        potencia_kw=75.0, tensao_nominal_v=380.0, planta="Planta São Paulo",
        area="Área de Compressores",
        observacoes="Motor principal do compressor 1.",
    ),
    Equipment(
        tag="MOT-002", modelo="M3BP 315", fabricante="ABB",
        potencia_kw=110.0, tensao_nominal_v=440.0, planta="Planta São Paulo",
        area="Área de Bombas",
        observacoes="Bomba de recalque da linha de utilidades.",
    ),
    Equipment(
        tag="MOT-003", modelo="SIMOTICS SD100", fabricante="Siemens",
        potencia_kw=45.0, tensao_nominal_v=380.0, planta="Planta Betim",
        area="Linha de Montagem",
        observacoes="Aciona a esteira principal.",
    ),
    Equipment(
        tag="MOT-004", modelo="NEMA Premium 254T", fabricante="WEG",
        potencia_kw=30.0, tensao_nominal_v=220.0, planta="Planta Manaus",
        area="Injeção Plástica",
        observacoes="Prensa injetora 4.",
    ),
]


def seed_if_empty() -> None:
    repo = EquipmentRepository()
    if not repo.list_all():
        for eq in SEED_EQUIPMENTS:
            repo.add(eq)
