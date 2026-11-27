"""Unit test 2 for library.loader.load_demands: asking for a week that is not in the file raises DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_demands

DATA_DIR = Path(__file__).parent / "data"


def test_2_load_demands():
    with pytest.raises(DataError, match="Period '2027-W2' not found") as error:
        load_demands("2027-W2", DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
