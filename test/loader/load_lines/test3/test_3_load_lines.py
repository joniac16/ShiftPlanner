"""Unit test 3 for library.loader.load_lines: two lines of the same restricted group with different limits raise DataError."""

from pathlib import Path

import pytest

from library.loader import DataError, load_lines

DATA_DIR = Path(__file__).parent / "data"


def test_3_load_lines():
    with pytest.raises(DataError, match="Restricted group 'RG1' has different limits on line L2") as error:
        load_lines(DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
