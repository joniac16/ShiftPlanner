"""Unit tests for library.periods.weeks_between."""

from library.periods import weeks_between


def test_same_period_is_zero():
    assert weeks_between("2027-W05", "2027-W05") == 0


def test_forward():
    assert weeks_between("2027-W01", "2027-W05") == 4


def test_backward_is_negative():
    assert weeks_between("2027-W05", "2027-W01") == -4


def test_across_year_with_53_weeks():
    assert weeks_between("2026-W52", "2027-W02") == 3
