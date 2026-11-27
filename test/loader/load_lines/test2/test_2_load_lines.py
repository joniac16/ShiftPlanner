"""Unit test 2 for library.loader.load_lines: a repeated line id raises DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_lines

DATA_DIR = Path(__file__).parent / "data"


def test_2_load_lines():
    with pytest.raises(DataError, match="Duplicate line id 'L1'") as error:
        load_lines(DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
