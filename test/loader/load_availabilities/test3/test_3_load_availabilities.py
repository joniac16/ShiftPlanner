"""Unit test 3 for library.loader.load_availabilities: an operator that appears twice in the same week raises DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_availabilities

DATA_DIR = Path(__file__).parent / "data"


def test_3_load_availabilities():
    with pytest.raises(DataError, match='Operator OP1 appears twice in 2027-W1') as error:
        load_availabilities("2027-W1", DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
