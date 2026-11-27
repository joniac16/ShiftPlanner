"""Unit tests for library.periods.sort_periods."""

from library.periods import sort_periods


def test_sorts_by_date_not_as_text():
    # As text, "2027-W10" would come before "2027-W2".
    assert sort_periods(["2027-W10", "2027-W2", "2027-W1"]) == ["2027-W1", "2027-W2", "2027-W10"]


def test_sorts_across_years():
    assert sort_periods(["2027-W1", "2026-W53", "2026-W9"]) == ["2026-W9", "2026-W53", "2027-W1"]


def test_empty_list():
    assert sort_periods([]) == []
