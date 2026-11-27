"""Unit test 4 for library.loader.load_history: an empty history folder returns an empty list."""

from pathlib import Path

from library.loader import load_history

DATA_DIR = Path(__file__).parent / "data"


def test_4_load_history():
    result = load_history(DATA_DIR)

    print(f"\nResult of load_history with no weeks: {result}")

    assert result == []
