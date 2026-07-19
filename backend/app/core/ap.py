"""Action Priority (AP) engine — AIAG-VDA FMEA Handbook 1st Ed. (2019), Step 5.

DŮLEŽITÉ (doménové pravidlo projektu):
    AP se NIKDY nepočítá LLM. Je to deterministická lookup funkce S x O x D.
    Tento modul je jediný zdroj pravdy.

Pozn. k licencím: samotná AP matice je logika (H/M/L), nikoli text tabulek.
Slovní kritéria S/O/D jsou v RatingCatalog jako parafráze / customer-supplied.

⚠️ Před produkčním nasazením ověřit celou matici proti licencované kopii
   AIAG-VDA FMEA Handbook 1st Ed. (2019), Table AP. Viz tests/test_ap.py.
"""
from __future__ import annotations

from typing import Literal

APLevel = Literal["H", "M", "L"]

_S_BANDS = ((9, 10), (7, 8), (4, 6), (2, 3), (1, 1))
_O_BANDS = ((8, 10), (6, 7), (4, 5), (2, 3), (1, 1))
_D_BANDS = ((7, 10), (5, 6), (2, 4), (1, 1))

# řádky = pásma S, sloupce = pásma O, buňka = 4 hodnoty dle pásem D
_AP_MATRIX: dict[tuple[int, int], tuple[APLevel, APLevel, APLevel, APLevel]] = {
    # S 9-10
    (0, 0): ("H", "H", "H", "H"),
    (0, 1): ("H", "H", "H", "H"),
    (0, 2): ("H", "H", "H", "M"),
    (0, 3): ("H", "M", "L", "L"),
    (0, 4): ("L", "L", "L", "L"),
    # S 7-8
    (1, 0): ("H", "H", "H", "H"),
    (1, 1): ("H", "H", "H", "M"),
    (1, 2): ("H", "M", "M", "M"),
    (1, 3): ("M", "M", "L", "L"),
    (1, 4): ("L", "L", "L", "L"),
    # S 4-6
    (2, 0): ("H", "M", "M", "M"),
    (2, 1): ("M", "M", "M", "L"),
    (2, 2): ("M", "M", "L", "L"),
    (2, 3): ("L", "L", "L", "L"),
    (2, 4): ("L", "L", "L", "L"),
    # S 2-3
    (3, 0): ("M", "M", "L", "L"),
    (3, 1): ("M", "L", "L", "L"),
    (3, 2): ("L", "L", "L", "L"),
    (3, 3): ("L", "L", "L", "L"),
    (3, 4): ("L", "L", "L", "L"),
    # S 1  — bez rizika, vždy L
    (4, 0): ("L", "L", "L", "L"),
    (4, 1): ("L", "L", "L", "L"),
    (4, 2): ("L", "L", "L", "L"),
    (4, 3): ("L", "L", "L", "L"),
    (4, 4): ("L", "L", "L", "L"),
}


def _band_index(value: int, bands: tuple[tuple[int, int], ...]) -> int:
    for idx, (lo, hi) in enumerate(bands):
        if lo <= value <= hi:
            return idx
    raise ValueError(f"hodnota {value} mimo rozsah 1-10")


def _validate(name: str, value: int) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} musí být int, dostal {type(value).__name__}")
    if not 1 <= value <= 10:
        raise ValueError(f"{name} musí být v rozsahu 1-10, dostal {value}")


def ap_lookup(severity: int, occurrence: int, detection: int) -> APLevel:
    """Vrátí Action Priority H / M / L. Deterministické, bez AI."""
    _validate("severity", severity)
    _validate("occurrence", occurrence)
    _validate("detection", detection)
    s = _band_index(severity, _S_BANDS)
    o = _band_index(occurrence, _O_BANDS)
    d = _band_index(detection, _D_BANDS)
    return _AP_MATRIX[(s, o)][d]


def requires_justification(ap: APLevel, has_actions: bool) -> bool:
    """High AP bez akce vyžaduje písemné zdůvodnění (auditní požadavek IATF)."""
    return ap == "H" and not has_actions
