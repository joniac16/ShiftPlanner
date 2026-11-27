"""Unit test 4 for library.loader.load_planning_input: an availability for an operator that does not exist raises DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_planning_input

DATA_DIR = Path(__file__).parent / "data"


def test_4_load_planning_input():
    with pytest.raises(DataError, match='Availability for 2027-W3 refers to operator OP9, which does not exist') as error:
        load_planning_input("2027-W3", DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
