"""Unit test 3 for library.loader.load_operators: a training level that is not specialist/qualified raises DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_operators

DATA_DIR = Path(__file__).parent / "data"


def test_3_load_operators():
    with pytest.raises(DataError, match="Operator OP1 has invalid level 'expert' on line L1") as error:
        load_operators(DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
