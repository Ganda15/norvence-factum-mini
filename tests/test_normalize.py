import json
from decimal import Decimal
from pathlib import Path

import pytest

from app.normalize import normalize_amount

FIXTURE = Path(__file__).parent / "fixtures" / "echantillons.jsonl"


def charger_cas():
    # une ligne du fichier = un cas de test (du JSON)
    lignes = FIXTURE.read_text(encoding="utf-8").splitlines()
    return [json.loads(ligne) for ligne in lignes if ligne.strip()]


CAS = charger_cas()


def test_normalize_plain_amount():
    assert normalize_amount("1250.00") == Decimal("1250.00")


@pytest.mark.parametrize("cas", CAS, ids=[cas["id"] for cas in CAS])
def test_normalize_echantillons(cas):
    resultat = normalize_amount(cas["montant_brut"])
    assert resultat == Decimal(cas["montant_attendu"])


def test_normalize_integer_input():
    assert normalize_amount(1250) == Decimal("1250.00")


def test_normalize_none():
    with pytest.raises(ValueError, match="absent"):
        normalize_amount(None)


def test_normalize_unreadable_text():
    with pytest.raises(ValueError, match="illisible"):
        normalize_amount("abc")
