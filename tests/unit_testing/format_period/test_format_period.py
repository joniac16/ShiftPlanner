"""Unit tests for library.periods.format_period."""

from datetime import date

from library.periods import format_period, parse_period


def test_pads_week_number_to_two_digits():
    assert format_period(date(2027, 2, 1)) == "2027-W05"


def test_any_day_of_the_week_gives_the_same_period():
    assert {format_period(date(2027, 2, d)) for d in range(1, 8)} == {"2027-W05"}


def test_uses_iso_year_not_calendar_year():
    # 1 January 2027 is a Friday, so it still belongs to 2026-W53.
    assert format_period(date(2027, 1, 1)) == "2026-W53"


def test_round_trip_with_parse_period():
    for period in ["2026-W01", "2026-W53", "2027-W05", "2027-W52"]:
        assert format_period(parse_period(period)) == period


def test_periods_sort_chronologically_as_text():
    periods = [format_period(date(2027, m, 1)) for m in range(1, 13)]
    assert sorted(periods) == periods
