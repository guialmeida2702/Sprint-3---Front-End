"""
Camada de acesso a dados dos equipamentos.

Hoje persiste em um arquivo JSON local para permitir o desenvolvimento do
Front-end de forma totalmente desacoplada do backend/modelo (conforme
exigido na Sprint 1). Quando o time de Backend/ML disponibilizar uma API
real, basta reimplementar os métodos desta classe (mantendo a mesma
assinatura) para consumir a API — nenhuma tela precisa ser alterada.
"""
import json
import os
from typing import List, Optional

from core.models import Equipment
from core.config import EQUIPMENT_FILE


class EquipmentRepository:
    def __init__(self, path: str = EQUIPMENT_FILE):
        self.path = path
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def list_all(self) -> List[Equipment]:
        with open(self.path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [Equipment.from_dict(r) for r in raw]

    def get(self, tag: str) -> Optional[Equipment]:
        for eq in self.list_all():
            if eq.tag == tag:
                return eq
        return None

    def exists(self, tag: str) -> bool:
        return self.get(tag) is not None

    def add(self, equipment: Equipment) -> None:
        data = [e.to_dict() for e in self.list_all()]
        data.append(equipment.to_dict())
        self._save(data)

    def update(self, equipment: Equipment) -> None:
        data = [
            equipment.to_dict() if e.tag == equipment.tag else e.to_dict()
            for e in self.list_all()
        ]
        self._save(data)

    def delete(self, tag: str) -> None:
        data = [e.to_dict() for e in self.list_all() if e.tag != tag]
        self._save(data)

    def _save(self, data: list) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
