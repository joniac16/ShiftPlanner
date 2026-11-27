"""Unit test 4 for library.graph.build_slot_set: no line runs that week.

Dummy data: the demands of 2027-W5 are empty, so there are no slots.
"""

from pathlib import Path

from library.graph import build_slot_set
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {}


def test_4_build_slot_set():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = build_slot_set(data)

    print(f"\nResult of build_slot_set for {data.period}: {len(result)} slots")
    for slot_id, slot in result.items():
        print(f"  {slot_id}: {slot}")

    assert result == EXPECTED
    assert list(result) == list(EXPECTED)  # same order
