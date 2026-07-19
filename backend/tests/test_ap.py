import pytest

from app.core.ap import ap_lookup, requires_justification


@pytest.mark.parametrize("s,o,d,expected", [
    (10, 10, 10, "H"),   # nejhorší možný případ
    (10, 1, 1, "L"),     # safety, ale vyloučený výskyt
    (9, 4, 1, "M"),
    (9, 2, 4, "L"),
    (8, 6, 1, "M"),
    (7, 2, 10, "M"),
    (5, 8, 10, "H"),
    (5, 2, 1, "L"),
    (3, 10, 10, "M"),
    (3, 4, 10, "L"),
    (1, 10, 10, "L"),    # bez dopadu -> vždy L
])
def test_known_cells(s, o, d, expected):
    assert ap_lookup(s, o, d) == expected


def test_full_matrix_coverage():
    for s in range(1, 11):
        for o in range(1, 11):
            for d in range(1, 11):
                assert ap_lookup(s, o, d) in {"H", "M", "L"}


def test_monotonicity_nondecreasing_with_worse_ratings():
    rank = {"L": 0, "M": 1, "H": 2}
    for s in range(1, 11):
        for o in range(1, 11):
            for d in range(1, 10):
                assert rank[ap_lookup(s, o, d + 1)] >= rank[ap_lookup(s, o, d)]
    for s in range(1, 11):
        for d in range(1, 11):
            for o in range(1, 10):
                assert rank[ap_lookup(s, o + 1, d)] >= rank[ap_lookup(s, o, d)]
    for o in range(1, 11):
        for d in range(1, 11):
            for s in range(1, 10):
                assert rank[ap_lookup(s + 1, o, d)] >= rank[ap_lookup(s, o, d)]


@pytest.mark.parametrize("bad", [0, 11, -1])
def test_out_of_range(bad):
    with pytest.raises(ValueError):
        ap_lookup(bad, 5, 5)


def test_type_validation():
    with pytest.raises(TypeError):
        ap_lookup(True, 5, 5)


def test_justification_rule():
    assert requires_justification("H", has_actions=False) is True
    assert requires_justification("H", has_actions=True) is False
    assert requires_justification("M", has_actions=False) is False
