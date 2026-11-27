"""Unit test 4 for library.loader.load_demands: an unknown role in staff raises DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_demands

DATA_DIR = Path(__file__).parent / "data"


def test_4_load_demands():
    with pytest.raises(DataError, match="Unknown role\\(s\\) \\['supervisor'\\]") as error:
        load_demands("2027-W1", DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
