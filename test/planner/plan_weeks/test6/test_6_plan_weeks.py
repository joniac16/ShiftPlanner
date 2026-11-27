"""Unit test 6 for library.planner.plan_weeks: a range that crosses the year.

Dummy data: L1 is in RG1 (max 1 week, rest 1), L2 is not restricted. Each
week L1 and L2 need 1 qualified in the morning.
  OP1 qualified on L1, specialist on L2 (on L2: specialist as qualified, weight 6)
  OP2 qualified on L1 and L2 (weight 10 on both)
  Both available every morning.
Without history, the best week is OP1 on L1 + OP2 on L2 (20; the swap is 16).
The week after, OP1 is blocked from RG1, so: OP2 on L1 + OP1 on L2 (16).

2026 has 53 ISO weeks, so planning 2026-W53 to 2027-W1 gives exactly those
two weeks, chained as in test1. The files are listed in data/history/.gitignore.
"""

from pathlib import Path

from library.planner import plan_weeks

DATA_DIR = Path(__file__).parent / "data"
HISTORY = DATA_DIR / "history"

EXPECTED_FILES = {
    "2026-W53.json": """{
  "period": "2026-W53",
  "assignments": [
    {"operator": "OP1", "line": "L1", "shift": "Morning", "role": "qualified"},
    {"operator": "OP2", "line": "L2", "shift": "Morning", "role": "qualified"}
  ]
}
""",
    "2027-W1.json": """{
  "period": "2027-W1",
  "assignments": [
    {"operator": "OP2", "line": "L1", "shift": "Morning", "role": "qualified"},
    {"operator": "OP1", "line": "L2", "shift": "Morning", "role": "qualified"}
  ]
}
""",
}


def test_6_plan_weeks():
    for name in EXPECTED_FILES:
        (HISTORY / name).unlink(missing_ok=True)

    results = plan_weeks(2026, 53, 2027, 1, data_dir=DATA_DIR)

    print(f"\nplan_weeks planned {len(results)} week(s):")
    for result in results:
        print(f"  {result.allocation.period}: " + ", ".join(
            f"{a.operator}->{a.line} {a.role}" for a in result.allocation.assignments)
            + f" | weight {result.total_weight}")

    assert [r.allocation.period for r in results] == ["2026-W53", "2027-W1"]
    for name, text in EXPECTED_FILES.items():
        assert (HISTORY / name).read_text() == text
