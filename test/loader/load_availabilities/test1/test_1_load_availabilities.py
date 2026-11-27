"""Unit test for library.loader.load_availabilities.

Dummy data: data/source/availabilities.json with two weeks. The test asks
for 2027-W2, so the result must contain only that week's availability:
  OP1  Morning, Night
  OP2  not available (empty list)
  OP3  Afternoon
"""

from pathlib import Path

from library.loader import load_availabilities
from library.models import Availability

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {
    "OP1": Availability(operator="OP1", shifts=["Morning", "Night"]),
    "OP2": Availability(operator="OP2", shifts=[]),
    "OP3": Availability(operator="OP3", shifts=["Afternoon"]),
}


def test_load_availabilities():
    result = load_availabilities("2027-W2", DATA_DIR)

    print("\nResult of load_availabilities for 2027-W2:")
    for operator_id, availability in result.items():
        print(f"  {operator_id}: {availability}")

    assert result == EXPECTED
