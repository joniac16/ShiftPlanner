"""Unit test 2 for library.loader.load_operators: a repeated operator id raises DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_operators

DATA_DIR = Path(__file__).parent / "data"


def test_2_load_operators():
    with pytest.raises(DataError, match="Duplicate operator id 'OP1'") as error:
        load_operators(DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
