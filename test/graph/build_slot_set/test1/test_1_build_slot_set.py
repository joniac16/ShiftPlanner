"""Unit test 1 for library.graph.build_slot_set: several slots of the same role.

Dummy data: in 2027-W5, L1 Morning needs 1 specialist, 2 qualified and 3
assistants, so the result has 6 slots, numbered from 1 within each role.
"""

from pathlib import Path

from library.graph import build_slot_set
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {
    "L1-Morning-specialist-1": {"line": "L1", "shift": "Morning", "role": "specialist"},
    "L1-Morning-qualified-1": {"line": "L1", "shift": "Morning", "role": "qualified"},
    "L1-Morning-qualified-2": {"line": "L1", "shift": "Morning", "role": "qualified"},
    "L1-Morning-assistant-1": {"line": "L1", "shift": "Morning", "role": "assistant"},
    "L1-Morning-assistant-2": {"line": "L1", "shift": "Morning", "role": "assistant"},
    "L1-Morning-assistant-3": {"line": "L1", "shift": "Morning", "role": "assistant"},
}


def test_1_build_slot_set():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = build_slot_set(data)

    print(f"\nResult of build_slot_set for {data.period}: {len(result)} slots")
    for slot_id, slot in result.items():
        print(f"  {slot_id}: {slot}")

    assert result == EXPECTED
    assert list(result) == list(EXPECTED)  # same order
