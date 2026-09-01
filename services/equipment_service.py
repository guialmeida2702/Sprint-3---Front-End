"""
Fachada entre o Front-end e a camada de dados (`data.repository`).
Concentra as regras de listagem/filtro para manter as telas simples.
"""
from typing import List, Optional

from core.models import Equipment
from data.repository import EquipmentRepository

_repo = EquipmentRepository()


def list_equipments() -> List[Equipment]:
    return _repo.list_all()


def get_equipment(tag: str) -> Optional[Equipment]:
    return _repo.get(tag)


def tag_exists(tag: str) -> bool:
    return _repo.exists(tag)


def register_equipment(equipment: Equipment) -> None:
    _repo.add(equipment)


def update_equipment(equipment: Equipment) -> None:
    _repo.update(equipment)


def filter_equipments(planta: str = None, area: str = None, texto: str = None) -> List[Equipment]:
    items = list_equipments()
    if planta and planta != "Todas":
        items = [e for e in items if e.planta == planta]
    if area and area != "Todas":
        items = [e for e in items if e.area == area]
    if texto:
        t = texto.lower().strip()
        if t:
            items = [
                e for e in items
                if t in e.tag.lower() or t in e.modelo.lower() or t in e.fabricante.lower()
            ]
    return items
