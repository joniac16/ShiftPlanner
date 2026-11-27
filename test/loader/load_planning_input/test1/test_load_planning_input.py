"""Unit test for library.loader.load_planning_input.

Dummy data:
  source/lines.json           L1, L2 (L2 in restricted group RG1)
  source/operators.json       OP1 (specialist L1, qualified L2), OP2 (qualified L1)
  source/demands.json         2027-W3: L1 Morning 1 specialist, L2 Night 1 qualified
  source/availabilities.json  2027-W3: OP1 Morning + Night, OP2 Morning
  history/                    2027-W1, 2027-W2 and 2027-W4

The test plans 2027-W3, so the history must contain only the weeks before
it (2027-W1 and 2027-W2), not 2027-W4.
"""

from pathlib import Path

from library.loader import load_planning_input
from library.models import (
    Assignment,
    Availability,
    Line,
    LineDemand,
    Operator,
    PlanningInput,
    RestrictedGroup,
    Shift,
    Staff,
    WeekAllocation,
)

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = PlanningInput(
    period="2027-W3",
    lines={
        "L1": Line(id="L1", name="Line 1", restricted_group=None),
        "L2": Line(id="L2", name="Line 2",
                   restricted_group=RestrictedGroup(id="RG1", max_consecutive_weeks=2, min_rest_weeks=1)),
    },
    operators={
        "OP1": Operator(id="OP1", name="Marie Curie", lines={"L1": "specialist", "L2": "qualified"}),
        "OP2": Operator(id="OP2", name="Isaac Newton", lines={"L1": "qualified"}),
    },
    demands=[
        LineDemand(line="L1", shifts=[Shift(name="Morning", staff=Staff(specialist=1, qualified=0, assistant=0))]),
        LineDemand(line="L2", shifts=[Shift(name="Night", staff=Staff(specialist=0, qualified=1, assistant=0))]),
    ],
    availabilities={
        "OP1": Availability(operator="OP1", shifts=["Morning", "Night"]),
        "OP2": Availability(operator="OP2", shifts=["Morning"]),
    },
    history=[
        WeekAllocation(period="2027-W1", assignments=[
            Assignment(operator="OP1", line="L2", shift="Night", role="qualified"),
        ]),
        WeekAllocation(period="2027-W2", assignments=[
            Assignment(operator="OP1", line="L2", shift="Night", role="qualified"),
        ]),
    ],
)


def test_load_planning_input():
    result = load_planning_input("2027-W3", DATA_DIR)

    print(f"\nResult of load_planning_input for {result.period}:")
    print("  lines:")
    for line in result.lines.values():
        print(f"    {line}")
    print("  operators:")
    for operator in result.operators.values():
        print(f"    {operator}")
    print("  demands:")
    for demand in result.demands:
        print(f"    {demand}")
    print("  availabilities:")
    for availability in result.availabilities.values():
        print(f"    {availability}")
    print("  history:")
    for week in result.history:
        print(f"    {week}")

    assert result == EXPECTED
