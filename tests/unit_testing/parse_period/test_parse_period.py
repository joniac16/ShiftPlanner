"""Unit tests for library.periods.parse_period."""

from datetime import date

import pytest

from library.periods import parse_period


def test_returns_monday_of_the_week():
    assert parse_period("2027-W5") == date(2027, 2, 1)


def test_first_week_can_start_in_previous_year():
    # ISO week 1 of 2026 starts on Monday 29 December 2025.
    assert parse_period("2026-W1") == date(2025, 12, 29)


def test_week_53_in_a_year_that_has_it():
    assert parse_period("2026-W53") == date(2026, 12, 28)


def test_week_53_in_a_year_without_it_raises():
    with pytest.raises(ValueError):
        parse_period("2027-W53")


def test_invalid_format_raises():
    with pytest.raises(ValueError):
        parse_period("2027-05")
