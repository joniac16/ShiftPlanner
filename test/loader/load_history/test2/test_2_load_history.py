"""Unit test 2 for library.loader.load_history: a file whose name does not match the period inside raises DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_history

DATA_DIR = Path(__file__).parent / "data"


def test_2_load_history():
    with pytest.raises(DataError, match="contains period '2027-W2', expected '2027-W1'") as error:
        load_history(DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
