"""Unit tests for library.periods.format_period."""

from datetime import date

from library.periods import format_period, parse_period


def test_week_number_has_no_leading_zero():
    assert format_period(date(2027, 2, 1)) == "2027-W5"


def test_any_day_of_the_week_gives_the_same_period():
    assert {format_period(date(2027, 2, d)) for d in range(1, 8)} == {"2027-W5"}


def test_uses_iso_year_not_calendar_year():
    # 1 January 2027 is a Friday, so it still belongs to 2026-W53.
    assert format_period(date(2027, 1, 1)) == "2026-W53"


def test_round_trip_with_parse_period():
    for period in ["2026-W1", "2026-W53", "2027-W5", "2027-W52"]:
        assert format_period(parse_period(period)) == period


def test_two_digit_week_number():
    assert format_period(date(2027, 3, 8)) == "2027-W10"
