"""Unit test 3 for library.loader.load_history: an invalid role in an assignment raises DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_history

DATA_DIR = Path(__file__).parent / "data"


def test_3_load_history():
    with pytest.raises(DataError, match="Invalid role 'supervisor' for operator OP1") as error:
        load_history(DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
