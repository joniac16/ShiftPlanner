"""Unit test 3 for library.loader.load_planning_input: a demand for a line that does not exist raises DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_planning_input

DATA_DIR = Path(__file__).parent / "data"


def test_3_load_planning_input():
    with pytest.raises(DataError, match='Demand for 2027-W3 refers to line L9, which does not exist') as error:
        load_planning_input("2027-W3", DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
