"""Unit test for library.loader.load_demands.

Dummy data: data/source/demands.json with two weeks. The test asks for
2027-W2, so the result must contain only that week's demand:
  L1  Morning (1 specialist, 2 qualified, 1 assistant), Night (1, 1, 0)
  L2  Afternoon (0, 1, 2)
"""

from pathlib import Path

from library.loader import load_demands
from library.models import LineDemand, Shift, Staff

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = [
    LineDemand(line="L1", shifts=[
        Shift(name="Morning", staff=Staff(specialist=1, qualified=2, assistant=1)),
        Shift(name="Night", staff=Staff(specialist=1, qualified=1, assistant=0)),
    ]),
    LineDemand(line="L2", shifts=[
        Shift(name="Afternoon", staff=Staff(specialist=0, qualified=1, assistant=2)),
    ]),
]


def test_load_demands():
    result = load_demands("2027-W2", DATA_DIR)

    print("\nResult of load_demands for 2027-W2:")
    for demand in result:
        print(f"  {demand.line}:")
        for shift in demand.shifts:
            print(f"    {shift}")

    assert result == EXPECTED
