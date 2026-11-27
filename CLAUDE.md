# ShiftPlanner

Automatic allocation of factory operators to production lines and shifts, using Google OR-Tools (CP-SAT).

## Conventions

- Everything committed to the repository is in **English**: code, comments, docstrings, JSON keys and values, README, commit messages.
- Python package with the project functions: `library/`. Unit tests (pytest): `tests/`, one `test_<module>.py` per module in `library/`.
- Tests must use small fixed data in `tests/fixtures/`, never the files in `data/source/`.
- Run tests with `python -m pytest`. Dependencies: `pip install -r requirements.txt`.

## Structure

```
library/
  models.py     Dataclasses (master: Line, RestrictedGroup, Operator;
                weekly: LineDemand, Shift, Staff, Availability)
  periods.py    ISO week helpers ("2026-W48"): parse, format, next, weeks_between
  loader.py     (empty) read/write the JSON files
  solver.py     (empty) OR-Tools allocation logic
tests/
data/
  source/
    lines.json, operators.json    Master data (change rarely)
    history.json                  Final allocations of past weeks
    weeks/<period>/               Weekly data, one folder per ISO week
      demand.json, availability.json
  output/       Generated allocations (proposals)
main.py         Entry point (placeholder)
```

## Data model (data/source)

Master data changes rarely; weekly data changes every week. To prepare a new
week, copy the previous week's folder and edit what changes.

### lines.json (master)
```json
{"id": "L3", "name": "Line 3", "restricted_group": {"id": "RG1", "max_consecutive_weeks": 2, "min_rest_weeks": 2}}
```
- `restricted_group` is optional (absent = no restriction). Weeks worked on **any** line of the same group (any shift, any role) count together: after `max_consecutive_weeks` in a row in the group, the operator must stay off all its lines for at least `min_rest_weeks`. All lines of a group must declare the same values; `loader.py` should validate this.

### operators.json (master)
```json
{"id": "OP1", "name": "Marie Curie", "lines": {"L3": "qualified", "L4": "qualified"}}
```
- Ids are `OP<n>` with no leading zeros.
- `lines` is the operator's training: line id -> `"specialist"` or `"qualified"`. A line not listed can only be covered as `"assistant"` (no training, there to help or learn).
- Sample names are famous historical figures (no living people).

### weeks/<period>/demand.json (weekly)
```json
{"line": "L1", "shifts": [{"name": "Morning", "staff": {"specialist": 1, "qualified": 3, "assistant": 1}}]}
```
- Shifts the line runs that week (open-ended list) and the exact number of operators of each role each shift needs. A line not listed does not run that week.

### weeks/<period>/availability.json (weekly)
```json
{"operator": "OP1", "shifts": ["Morning", "Weekend"]}
```
- Shifts the operator can cover that week. All are treated equally (no regular/volunteer distinction, by decision). Empty list or missing operator = not available (holidays, sick leave...).

### history.json
```json
{"period": "2026-W44", "assignments": [{"operator": "OP33", "line": "L1", "shift": "Morning", "role": "specialist"}]}
```
- Final (applied) allocation per planning period. `data/output/` holds proposals; `history.json` holds what was actually used.
- Stores the `role`, so later training changes in `operators.json` do not alter the past.
- Periods are ISO weeks as strings `YYYY-Www` (zero-padded, sorts chronologically). Never do integer arithmetic on them; use `library/periods.py` (some years have 53 ISO weeks, e.g. 2026).
- Only ids are stored; names and training come from `operators.json`.

## Sample data

- 5 lines, 65 operators. Weekly folders 2026-W44 to 2026-W47 (53 positions, history available) and 2026-W48 (51 positions, two absences: OP8, OP27), the first week to be planned by the solver. L3 and L5 form restricted group RG1.
- Sample data must stay **feasible**: whenever master data, weekly data or rules change, check with OR-Tools that every week can be fully covered and that the history complies with all rules, using each week's own demand and availability (coverage, availability, roles, one assignment per operator per week, restricted groups). Restricted groups need a wide enough trained pool to rotate.
- When planning the next week, the solver must take the end of `history.json` into account for restricted groups (e.g. an operator with two consecutive weeks in RG1 must rest).

## Open questions (ask the user before writing the solver)

1. Can an operator cover more than one shift in the same week? Sample data and history assume **at most one**.
2. Can a position be covered by a higher level (specialist in a qualified slot, qualified in an assistant slot)? Sample data assumes **exact roles only**.

## Ideas discussed, not implemented

- Fair distribution of nights/weekends using history, global night-shift rotation (possibly in a future `rules.json`), hard vs. soft constraints (soft ones as penalties in the objective).
