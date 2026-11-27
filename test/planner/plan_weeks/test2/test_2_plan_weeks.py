"""Unit test 2 for library.planner.plan_weeks: if a week fails, nothing is saved.

Dummy data: L1 is in RG1 (max 1 week, rest 1), L2 is not restricted. Each
week L1 and L2 need 1 qualified in the morning.
  OP1 qualified on L1, specialist on L2 (on L2: specialist as qualified, weight 6)
  OP2 qualified on L1 and L2 (weight 10 on both)
  Both available every morning.
Without history, the best week is OP1 on L1 + OP2 on L2 (20; the swap is 16).
The week after, OP1 is blocked from RG1, so: OP2 on L1 + OP1 on L2 (16).
  demands.json has no 2027-W6.

Planning 2027-W5 to 2027-W6 fails on W6: DataError says which week failed,
and no file is written, not even W5 (which could be planned).
"""

from pathlib import Path

import pytest

from library.loader import DataError
from library.planner import plan_weeks

DATA_DIR = Path(__file__).parent / "data"
HISTORY = DATA_DIR / "history"


def test_2_plan_weeks():
    with pytest.raises(DataError, match=r"Error planning 2027-W6 \(nothing was saved\): Period '2027-W6' not found") as error:
        plan_weeks(2027, 5, 2027, 6, data_dir=DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")

    assert not (HISTORY / "2027-W5.json").exists()
    assert not (HISTORY / "2027-W6.json").exists()
