"""Unit test for library.loader.load_lines.

Dummy data: data/source/lines.json
  L1  no restricted group
  L2  restricted group RG1 (max 2 consecutive weeks, min 3 rest weeks)
  L3  restricted group RG1 (same values)
"""

from pathlib import Path

from library.loader import load_lines
from library.models import Line, RestrictedGroup

DATA_DIR = Path(__file__).parent / "data"

RG1 = RestrictedGroup(id="RG1", max_consecutive_weeks=2, min_rest_weeks=3)

EXPECTED = {
    "L1": Line(id="L1", name="Line 1", restricted_group=None),
    "L2": Line(id="L2", name="Line 2", restricted_group=RG1),
    "L3": Line(id="L3", name="Line 3", restricted_group=RG1),
}


def test_load_lines():
    result = load_lines(DATA_DIR)

    print("\nResult of load_lines:")
    for line_id, line in result.items():
        print(f"  {line_id}: {line}")

    assert result == EXPECTED
