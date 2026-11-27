"""Unit test 2 for library.graph.build_slot_set: roles with 0 positions give no slot.

Dummy data: in 2027-W5, L1 Morning needs 0 specialists, 2 qualified and 0
assistants, and L1 Night needs nobody. Only the 2 qualified slots appear.
"""

from pathlib import Path

from library.graph import build_slot_set
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {
    "L1-Morning-qualified-1": {"line": "L1", "shift": "Morning", "role": "qualified"},
    "L1-Morning-qualified-2": {"line": "L1", "shift": "Morning", "role": "qualified"},
}


def test_2_build_slot_set():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = build_slot_set(data)

    print(f"\nResult of build_slot_set for {data.period}: {len(result)} slots")
    for slot_id, slot in result.items():
        print(f"  {slot_id}: {slot}")

    assert result == EXPECTED
    assert list(result) == list(EXPECTED)  # same order
