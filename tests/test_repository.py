"""Testes de data/repository.py — camada de persistência (JSON local,
substituível por uma API real sem alterar a assinatura pública)."""
import os

from core.models import Equipment
from data.repository import EquipmentRepository


def _equipment(tag="T1", modelo="M"):
    return Equipment(
        tag=tag, modelo=modelo, fabricante="F", potencia_kw=1,
        tensao_nominal_v=220, planta="P", area="A",
    )


def test_repository_starts_empty(tmp_path):
    repo = EquipmentRepository(path=str(tmp_path / "eq.json"))
    assert repo.list_all() == []


def test_repository_creates_file_and_directory_from_custom_path(tmp_path):
    # Garante que o repositório respeita o diretório do "path" recebido,
    # e não sempre um diretório fixo (bug corrigido durante os testes).
    custom_path = tmp_path / "subpasta" / "eq.json"
    EquipmentRepository(path=str(custom_path))
    assert custom_path.exists()


def test_repository_does_not_touch_default_storage_dir(tmp_path, monkeypatch):
    # Roda em um CWD temporário: se o bug antigo (makedirs em um diretório
    # fixo) reaparecer, uma pasta "data/storage" seria criada aqui.
    monkeypatch.chdir(tmp_path)
    EquipmentRepository(path=str(tmp_path / "isolado" / "eq.json"))
    assert not os.path.exists(tmp_path / "data")


def test_repository_add_get_exists(tmp_path):
    repo = EquipmentRepository(path=str(tmp_path / "eq.json"))
    repo.add(_equipment("T1"))
    assert repo.exists("T1")
    assert not repo.exists("T-INEXISTENTE")
    assert repo.get("T1").modelo == "M"
    assert repo.get("T-INEXISTENTE") is None


def test_repository_add_multiple(tmp_path):
    repo = EquipmentRepository(path=str(tmp_path / "eq.json"))
    repo.add(_equipment("T1"))
    repo.add(_equipment("T2"))
    assert {e.tag for e in repo.list_all()} == {"T1", "T2"}


def test_repository_update_replaces_only_matching_tag(tmp_path):
    repo = EquipmentRepository(path=str(tmp_path / "eq.json"))
    repo.add(_equipment("T1", modelo="Antigo"))
    repo.add(_equipment("T2", modelo="Outro"))

    atualizado = _equipment("T1", modelo="Novo")
    repo.update(atualizado)

    assert repo.get("T1").modelo == "Novo"
    assert repo.get("T2").modelo == "Outro"
    assert len(repo.list_all()) == 2


def test_repository_delete(tmp_path):
    repo = EquipmentRepository(path=str(tmp_path / "eq.json"))
    repo.add(_equipment("T1"))
    repo.delete("T1")
    assert not repo.exists("T1")
    assert repo.list_all() == []


def test_repository_persists_across_instances(tmp_path):
    path = str(tmp_path / "eq.json")
    EquipmentRepository(path=path).add(_equipment("T9"))
    reopened = EquipmentRepository(path=path)
    assert reopened.exists("T9")
