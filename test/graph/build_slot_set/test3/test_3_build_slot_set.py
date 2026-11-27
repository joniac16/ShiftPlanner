"""Unit test 3 for library.graph.build_slot_set: several lines and shifts.

Dummy data: in 2027-W5, L2 runs Night (1 specialist, 1 qualified) and
Morning (1 assistant), and L1 runs Afternoon (1 specialist, 1 assistant).
The slots follow the order of the demands (L2 Night, L2 Morning, L1
Afternoon) and, within a shift, specialist, qualified, assistant.
"""

from pathlib import Path

from library.graph import build_slot_set
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {
    "L2-Night-specialist-1": {"line": "L2", "shift": "Night", "role": "specialist"},
    "L2-Night-qualified-1": {"line": "L2", "shift": "Night", "role": "qualified"},
    "L2-Morning-assistant-1": {"line": "L2", "shift": "Morning", "role": "assistant"},
    "L1-Afternoon-specialist-1": {"line": "L1", "shift": "Afternoon", "role": "specialist"},
    "L1-Afternoon-assistant-1": {"line": "L1", "shift": "Afternoon", "role": "assistant"},
}


def test_3_build_slot_set():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = build_slot_set(data)

    print(f"\nResult of build_slot_set for {data.period}: {len(result)} slots")
    for slot_id, slot in result.items():
        print(f"  {slot_id}: {slot}")

    assert result == EXPECTED
    assert list(result) == list(EXPECTED)  # same order
