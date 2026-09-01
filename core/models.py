"""
Modelos de dados (schemas) usados pela aplicação. Usar dataclasses aqui
garante um contrato único e tipado entre a camada de dados, os serviços
e as telas — qualquer alteração de campo é sentida em um único lugar.
"""
from dataclasses import dataclass, asdict, field, fields
from datetime import datetime
from typing import Optional


@dataclass
class Equipment:
    tag: str
    modelo: str
    fabricante: str
    potencia_kw: float
    tensao_nominal_v: float
    planta: str
    area: str
    data_cadastro: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
    imagem_placa_b64: Optional[str] = None
    observacoes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Equipment":
        # Ignora chaves desconhecidas propositalmente: se o schema evoluir
        # em uma sprint futura (novos campos) e um arquivo de dados mais
        # antigo (ou de uma versão futura) for carregado, não queremos que
        # o app quebre com um TypeError por causa de um campo extra/removido.
        known_fields = {f.name for f in fields(Equipment)}
        filtered = {k: v for k, v in d.items() if k in known_fields}
        return Equipment(**filtered)
