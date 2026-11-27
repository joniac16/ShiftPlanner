"""Unit test 2 for library.loader.load_availabilities: asking for a week that is not in the file raises DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_availabilities

DATA_DIR = Path(__file__).parent / "data"


def test_2_load_availabilities():
    with pytest.raises(DataError, match="Period '2027-W2' not found") as error:
        load_availabilities("2027-W2", DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
