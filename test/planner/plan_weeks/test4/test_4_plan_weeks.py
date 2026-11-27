"""Unit test 4 for library.planner.plan_weeks: overwrite=True replaces weeks of the range.

Dummy data: L1 is in RG1 (max 1 week, rest 1), L2 is not restricted. Each
week L1 and L2 need 1 qualified in the morning.
  OP1 qualified on L1, specialist on L2 (on L2: specialist as qualified, weight 6)
  OP2 qualified on L1 and L2 (weight 10 on both)
  Both available every morning.
Without history, the best week is OP1 on L1 + OP2 on L2 (20; the swap is 16).
The week after, OP1 is blocked from RG1, so: OP2 on L1 + OP1 on L2 (16).

The test first writes old versions of 2027-W5 and 2027-W6 (OP2 on L1 both
weeks, which would block OP2 from RG1). With overwrite=True they are replaced,
and the old W5 is not used to plan W6: the result is the same as in test1.
The files are listed in data/history/.gitignore.
"""

from pathlib import Path

from library.planner import plan_weeks

DATA_DIR = Path(__file__).parent / "data"
HISTORY = DATA_DIR / "history"

OLD = """{
  "period": "@P@",
  "assignments": [
    {"operator": "OP2", "line": "L1", "shift": "Morning", "role": "qualified"},
    {"operator": "OP1", "line": "L2", "shift": "Morning", "role": "qualified"}
  ]
}
"""

EXPECTED_FILES = {
    "2027-W5.json": """{
  "period": "2027-W5",
  "assignments": [
    {"operator": "OP1", "line": "L1", "shift": "Morning", "role": "qualified"},
    {"operator": "OP2", "line": "L2", "shift": "Morning", "role": "qualified"}
  ]
}
""",
    "2027-W6.json": """{
  "period": "2027-W6",
  "assignments": [
    {"operator": "OP2", "line": "L1", "shift": "Morning", "role": "qualified"},
    {"operator": "OP1", "line": "L2", "shift": "Morning", "role": "qualified"}
  ]
}
""",
}


def test_4_plan_weeks():
    for name in EXPECTED_FILES:
        (HISTORY / name).write_text(OLD.replace("@P@", name.removesuffix(".json")))

    results = plan_weeks(2027, 5, 2027, 6, data_dir=DATA_DIR, overwrite=True)

    print(f"\nplan_weeks planned {len(results)} week(s):")
    for result in results:
        print(f"  {result.allocation.period}: " + ", ".join(
            f"{a.operator}->{a.line} {a.role}" for a in result.allocation.assignments)
            + f" | weight {result.total_weight}")

    for name, text in EXPECTED_FILES.items():
        assert (HISTORY / name).read_text() == text
