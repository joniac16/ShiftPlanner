"""Unit tests for library/periods.py."""

from datetime import date

import pytest

from library.periods import format_period, next_period, parse_period, weeks_between


def test_parse_period_returns_monday():
    assert parse_period("2026-W48") == date(2026, 11, 23)


def test_format_period_pads_week_number():
    assert format_period(date(2026, 3, 2)) == "2026-W10"
    assert format_period(date(2026, 1, 5)) == "2026-W02"


def test_format_period_uses_iso_year():
    # 1 January 2027 is a Friday, so it still belongs to 2026-W53.
    assert format_period(date(2027, 1, 1)) == "2026-W53"


def test_parse_and_format_round_trip():
    assert format_period(parse_period("2026-W53")) == "2026-W53"


def test_next_period():
    assert next_period("2026-W48") == "2026-W49"


def test_next_period_crosses_year_with_53_weeks():
    assert next_period("2026-W52") == "2026-W53"
    assert next_period("2026-W53") == "2027-W01"


def test_next_period_crosses_year_with_52_weeks():
    assert next_period("2027-W52") == "2028-W01"


def test_next_period_backwards():
    assert next_period("2027-W01", -1) == "2026-W53"


def test_weeks_between():
    assert weeks_between("2026-W48", "2027-W02") == 7
    assert weeks_between("2026-W48", "2026-W48") == 0
    assert weeks_between("2026-W48", "2026-W44") == -4


def test_invalid_period_raises():
    with pytest.raises(ValueError):
        parse_period("2026-W54")
