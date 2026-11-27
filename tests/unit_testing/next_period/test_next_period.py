"""Unit tests for library.periods.next_period."""

from library.periods import next_period


def test_next_week():
    assert next_period("2027-W5") == "2027-W6"


def test_several_weeks_forward():
    assert next_period("2027-W5", 3) == "2027-W8"


def test_backwards():
    assert next_period("2027-W5", -1) == "2027-W4"


def test_crosses_year_with_53_weeks():
    assert next_period("2026-W52") == "2026-W53"
    assert next_period("2026-W53") == "2027-W1"


def test_crosses_year_with_52_weeks():
    assert next_period("2027-W52") == "2028-W1"


def test_backwards_across_year():
    assert next_period("2027-W1", -1) == "2026-W53"


def test_zero_weeks_returns_same_period():
    assert next_period("2027-W5", 0) == "2027-W5"
