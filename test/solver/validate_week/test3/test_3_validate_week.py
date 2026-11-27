"""Unit test 3 for library.solver.validate_week: an operator assigned twice.

Dummy data (the same in every validate_week test), week 2027-W5:
  Lines: L1 in RG1 (max 1 week, rest 1), L2, L3 (L3 does not run this week).
  Demand: L1 Morning 1 qualified + 1 assistant, L1 Night 1 qualified,
          L2 Morning 1 specialist.
  OP1 qualified L1, morning      OP2 specialist L2, morning + night
  OP3 no training, morning       OP4 qualified L1, morning, worked L1 in W4
  OP5 qualified L1, not available this week                 (blocked from RG1)
"""

from pathlib import Path

import pytest

from library.loader import DataError, load_planning_input
from library.models import Assignment, WeekAllocation
from library.solver import validate_week

DATA_DIR = Path(__file__).parent / "data"

ALLOCATION = WeekAllocation(period="2027-W5", assignments=[
    Assignment(operator="OP3", line="L1", shift="Morning", role="assistant"),
    Assignment(operator="OP3", line="L2", shift="Morning", role="assistant"),
])


def test_3_validate_week():
    data = load_planning_input("2027-W5", DATA_DIR)

    with pytest.raises(DataError, match='Operator OP3 is assigned more than once') as error:
        validate_week(ALLOCATION, data)

    print(f"\nDataError raised as expected: {error.value}")
