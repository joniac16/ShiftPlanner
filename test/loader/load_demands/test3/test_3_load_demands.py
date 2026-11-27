"""Unit test 3 for library.loader.load_demands: a line that appears twice in the same week raises DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_demands

DATA_DIR = Path(__file__).parent / "data"


def test_3_load_demands():
    with pytest.raises(DataError, match='Line L1 appears twice in 2027-W1') as error:
        load_demands("2027-W1", DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
