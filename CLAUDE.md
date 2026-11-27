# ShiftPlanner

Automatic allocation of factory operators to production lines and shifts, modelled as a **bipartite graph matching** problem and solved with NetworkX. This is a master's thesis (TFM) project: the graph approach was chosen so the theory can be explained in the thesis.

## Branches and environments

| Branch | Environment | Use |
|---|---|---|
| `dev` | development | **All work happens here** (new functions, fixes, docs). May be unfinished. |
| `test` | testing | A version that should already work, to be checked (tests + app) before release. |
| `main` | production | The stable version. Only receives what has passed through `test`. |

- Changes always flow in one direction: `dev` -> `test` -> `main`, by merge (preferably GitHub Pull Requests).
- **Never commit directly to `test` or `main`.** If a problem shows up in `test`, fix it in `dev` and merge again.
- Claude works **only on `dev`** (user decision). Merging `dev` into `test`, or `test` into `main`, is done only when the user asks.
- All branches contain the whole repository (code, tests, docs, this file). Production is defined by what runs (`app.py`), not by removing files; a clean package can be made with `.gitattributes` `export-ignore` + `git archive` if ever needed.
- Planned weeks generated in `data/history/` are not committed in any branch (they would travel to `main` with the merges) unless the user asks.

## Conventions

- Everything committed to the repository is in **English**: code, comments, docstrings, JSON keys and values, README, commit messages.
- **Never write numbers with leading zeros** (ids `OP1`, `L1`, periods `2027-W5`, file names `2027-W5.json`), by user preference.
- **Work step by step, one function at a time**, as the user asks. Do only what is requested in each step; if something else seems needed (other files, extra functions, data changes), say so and ask before doing it.
- Python package with the project functions: `library/`.
- Unit tests (pytest) live in `test/<module>/<function>/testX/` (`test1`, `test2`, ...: one folder per case; test1 is the valid case, the others usually error cases). Each `testX/` has a `test_X_<function>.py` file (e.g. `test_2_load_lines.py`; file names must be unique for pytest) and a `data/` folder with dummy data made for that case. `data/` mirrors the layout of the real `data/` folder (`source/`, `history/`), so the function under test receives the test's `data/` folder as its data directory. Tests must check that the function's result is coherent, and must never read the real `data/`.
- Every new function in `library/` gets its own test folder, except the small helpers in `library/utils.py`, which have no tests (user decision).
- Tests of functions that **write files** (e.g. `save_week`) write into their own `testX/data/` folder, so the result can be opened after the run: the test first deletes the file it is going to generate (to always start from the same state), and a `.gitignore` next to it lists that file so it is never committed.
- Run tests with `python -m pytest` (configured in `pytest.ini`). Dependencies: `pip install -r requirements.txt`.
- All data in the repository is simulated for now (no real personal data).

## Structure

```
library/
  models.py     Dataclasses (master: Line, RestrictedGroup, Operator;
                weekly: LineDemand, Shift, Staff, Availability;
                allocations: Assignment, WeekAllocation; solver input: PlanningInput;
                graph: MatchWeights; solver output: PlanningResult)
  utils.py      Small helpers: make_iso_week, next_iso_week, iso_week_to_date, sort_iso_weeks
  loader.py     Reads the JSON files into models (see "Loader" below)
  graph.py      Builds the bipartite graph from the PlanningInput (see "Solver" below)
  solver.py     Matching with NetworkX (see "Solver" below)
  writer.py     Writes the algorithm's results: save_week -> data/history/<period>.json
  planner.py    plan_weeks: plans a range of weeks in a row (see "Planning several weeks")
test/
  loader/<function>/testX/        test_X_<function>.py + data/ (dummy data)
  graph/, solver/, writer/, planner/ <function>/testX/   same layout
data/                             Simulated data, committed (source/ + history W1-W4). The app and main.py read
                                  and write here: planning adds files to data/history/ (user decision: no
                                  separate sample_data/ folder and no .gitignore in data/).
  source/                         Input prepared by the user
    lines.json, operators.json    Master data (change rarely)
    demands.json                  Weekly data: line needs, keyed by period
    availabilities.json           Weekly data: operator shifts, keyed by period
  history/<period>.json           Planned weeks: written by the solver, read back for later weeks
  backup/source/, backup/history/ Untouched copy of the original source/ and history/ (user request), to restore
                                  them after experimenting. Never read or written by the code; do not plan with
                                  data/backup as data folder.
main.py         Command line: parses arguments and calls plan_weeks
app.py          Front end (Streamlit): Plan, Schedule, Data and Graph screens
```

## Loader (`library/loader.py`)

Every function takes the data folder as a parameter (`data` by default); tests pass their own `data/` folder. Errors in the data raise `DataError` with a clear message.

| Function | Returns | Raises DataError if |
|---|---|---|
| `load_lines(data_dir)` | `dict[str, Line]` | repeated line id; lines of the same restricted group with different limits |
| `load_operators(data_dir)` | `dict[str, Operator]` | repeated operator id; training level not `specialist`/`qualified` |
| `load_demands(period, data_dir)` | `list[LineDemand]` (that week only) | week not in the file; line twice in the week; unknown role in `staff` |
| `load_availabilities(period, data_dir)` | `dict[str, Availability]` (that week only) | week not in the file; operator twice in the week |
| `load_history(data_dir)` | `list[WeekAllocation]`, chronological (`sort_iso_weeks`) | file name does not match the period inside; invalid role |
| `load_planning_input(period, data_dir)` | `PlanningInput` for the solver | operator trained on, or demand for, an unknown line; availability for an unknown operator |

`load_planning_input` calls the other five and keeps only the history weeks **before** `period`.

Tests: `test1` is the valid case of each function (expected result compared with `==`, result printed to the console); `test2`, `test3`... check each `DataError` (and that an empty history returns `[]`). Run with `python -m pytest -v -s`. Writing is in `writer.py` (see below).

## Solver (decisions)

Approach: bipartite graph, maximum-cardinality matching with maximum total weight (`networkx.max_weight_matching(G, maxcardinality=True)`): first cover as many slots as possible, then prefer the heaviest assignments. Implemented with **NetworkX only** (no own matching algorithm; `networkx` is in `requirements.txt`).
- Planned solver signature: `solve(data, weights=None, maximize_matches=True)`. `maximize_matches=True` -> maximum number of covered slots, then maximum weight among those (`maxcardinality=True`); `False` -> maximum weight only, even if fewer slots are covered.

- Left side: operators available that week (`build_operator_set`). Right side: slots, one node per position (e.g. 2 qualified needed -> 2 slots). Edges: an operator can take a slot, with a weight.
- **Each operator covers at most one slot per week.**
- **Always return a proposal**, even if not every slot can be covered; report the uncovered slots.
- **Assignment rules** (operator level on the line -> slots they can take):

  | Operator level on the line | Can take a slot of |
  |---|---|
  | specialist | specialist, qualified, assistant |
  | qualified | qualified, specialist (last resort), assistant |
  | no training on that line | assistant only |

  Any operator can be an assistant on any running line, but it wastes training, so it should only happen when operators are left over.
- **Weights** are parameters, easy to change to experiment: `MatchWeights` in `models.py`. One weight per (slot role, who fills it) (user decision, replacing the earlier "exact level" weights):

  | Field | Slot filled | Default |
  |---|---|---|
  | `specialist_slot_specialist` | specialist slot by a specialist | 10 |
  | `specialist_slot_qualified` | specialist slot by a qualified operator (last resort) | 1 |
  | `qualified_slot_qualified` | qualified slot by a qualified operator | 10 |
  | `qualified_slot_specialist` | qualified slot by a specialist | 6 |
  | `assistant_slot_untrained` | assistant slot by an operator untrained on the line | 10 |
  | `assistant_slot_trained` | assistant slot by a specialist or qualified operator (waste of training) | 3 |

  Usage: `build_edges(data, operator_set, slot_set, MatchWeights(specialist_slot_qualified=0.5))`. Weights only decide among matchings that cover the same number of slots: who takes each slot and, when operators are missing, which slots stay empty.
- **Restricted groups block every role**: an operator who must rest from a group cannot go to any of its lines, not even as an assistant. Rule (`get_blocked_groups`): blocked if the last run of consecutive weeks in the group lasted at least `max_consecutive_weeks` and fewer than `min_rest_weeks` weeks have passed since it ended. A week with no history counts as not worked.
- The history stores the **role of the slot** taken, not the operator's level.
- New models (slots, weights) go in `models.py`.

### graph.py

| Function | Returns |
|---|---|
| `get_blocked_groups(data)` | operator id -> set of restricted group ids they are blocked from that week |
| `build_operator_set(data)` | operator id -> `{"shifts": [...], "lines": {line id: [roles]}}`: available operators, every running line they can go to with **all the slot roles** they can take there (following the assignment rules, `ALLOWED_ROLES`), blocked lines removed; operators with no shifts or no possible line left out |
| `build_slot_set(data)` | slot id -> `{"line", "shift", "role"}`: one slot (graph node) per position needed in the week's demands, ids like `L1-Morning-qualified-2` (numbered from 1); roles with 0 positions give no slot; order of the demands, then specialist, qualified, assistant |
| `build_edges(data, operator_set, slot_set, weights=None)` | list of `(operator id, slot id, weight)`, ready for `G.add_weighted_edges_from`: an edge when the slot's shift is in the operator's shifts, its line in the operator's lines and its role among the operator's roles there; weight by operator level (from `data.operators`) and slot role, using `MatchWeights` (defaults if None) |
| `build_graph(data, weights=None)` | `networkx.Graph`: operator nodes (`bipartite=0`, attributes `shifts`, `lines`), slot nodes (`bipartite=1`, attributes `line`, `shift`, `role`; slots with no candidate included, with no edges) and the weighted edges (`weight` attribute) |

Both sets are plain dicts (id -> attributes), ready for `G.add_nodes_from(set.items(), bipartite=0/1)`; no extra model is needed. Operator and slot ids never clash (`OP1` vs `L1-...`).

Each function has its tests in `test/graph/<function>/testX/`.

### solver.py

| Function | Returns |
|---|---|
| `find_matching(graph, maximize_matches=True)` | dict slot id -> operator id (order of the slots in the graph), from `networkx.max_weight_matching(graph, maxcardinality=maximize_matches)` |
| `build_allocation(period, matching, graph)` | `WeekAllocation`: one `Assignment` per pair, with the slot's line, shift and **role** (taken from the slot node); order of the matching |
| `solve(data, weights=None, maximize_matches=True)` | `PlanningResult`: builds the graph, finds the matching, builds the allocation and the report. Always returns a plan; writes nothing to disk |
| `validate_week(allocation, data)` | nothing; raises DataError if the allocation breaks a rule (see below) |

`PlanningResult` (models.py), the output of `solve`: `allocation` (WeekAllocation, the week's plan), `uncovered_slots` (slot id -> number of candidate operators it had), `unassigned_operators` (available operators who got no slot), `total_weight`.

In `uncovered_slots`, 0 candidates means nobody could take the slot; more than 0 means its candidates were needed elsewhere. A Hall's theorem explanation is a possible later improvement.

`validate_week(allocation, data)` (solver.py) raises DataError unless every assignment has: a known operator, assigned only once; available that week and on that shift; a line that runs that week and runs that shift; no block from the line's restricted group; a role allowed for the operator's level (`ALLOWED_ROLES`). No (line, shift, role) may have more operators than the demand; fewer is allowed.

### writer.py

| Function | Does |
|---|---|
| `save_week(allocation, data_dir, overwrite=False)` | validates with `validate_week` (against `load_planning_input` of that week) and writes `history/<period>.json` (one assignment per line). DataError if invalid (nothing written) or if the week exists and `overwrite` is False. If later weeks exist, prints a warning and saves anyway. Returns the path |

Simulated week 2027-W5 with `solve`: 48 of 48 slots covered, all with the exact level (total weight 480, a few ms); 15 of the 63 available operators left unassigned.

## Planning several weeks (`library/planner.py`, `main.py`)

`plan_weeks(start_year, start_week, end_year, end_week, data_dir="data", weights=None, maximize_matches=True, overwrite=False)` -> list of `PlanningResult` (one per week). It is the loop used by `main.py` and meant to be called directly by a future front end (weeks are given as year + week number, by user choice, to make the front end easier).

1. Loads the whole history into memory. If a week of the range is already in it and `overwrite` is False -> DataError before planning anything; with `overwrite`, those weeks are dropped from the in-memory history (the old versions are not used).
2. Week by week: `load_planning_input`, replace its history with the in-memory one (weeks before it), `solve`, `validate_week`, and append the allocation to the in-memory history, so the next week sees it (restricted groups).
3. Only if every week was planned, saves them all with `save_week` (all or nothing: if a week fails, DataError says which one and **no file is written**).

There is no `data/output/` folder and no separate approval step (user decision): planned weeks go straight to `data/history/`. To change a planned week, edit its file or plan it again with `overwrite`. When overwriting a range, `save_week` warns about later weeks that the same run is about to replace (harmless; left as is for now).

Command line (`main.py` only parses arguments and calls `plan_weeks`; it has no tests):

    python main.py --start-year 2027 --start-week 5 --end-year 2027 --end-week 8
        [--data-dir data] [--maximize matches|weight] [--overwrite]
        [--specialist-slot-specialist 10] [--specialist-slot-qualified 1]
        [--qualified-slot-qualified 10] [--qualified-slot-specialist 6]
        [--assistant-slot-untrained 10] [--assistant-slot-trained 3]

Exit code 0 and a summary per week (assignments, uncovered slots, unassigned operators, total weight); on DataError, the message and exit code 1.

## Front end (`app.py`)

Streamlit app, started with `streamlit run app.py`. Like `main.py`, it only displays data and calls `library/` functions, so it has no tests. Its texts are in English (repository convention). Sidebar: screen and data folder (default `data`; if it has no `source/`, it only shows an error saying there is no data).

| Screen | Shows |
|---|---|
| Plan | form with start/end year and week (default: the source weeks not in the history yet), objective, overwrite and the six weights; calls `plan_weeks` and shows, per week, assignments, uncovered slots (with candidates), unassigned operators and total weight. Errors and `save_week` warnings are shown in the page |
| Schedule | a history week as a lines x shifts table with names and roles, coverage against that week's demand (covered / needed), and all assignments with each operator's level on the line |
| Data | operators with their level per line, lines with their restricted group, and a week's demand and availability |
| Graph | the bipartite graph of a week limited to the chosen lines and shifts (operators left, slots right), drawn with matplotlib, with the matching's edges in red; for the thesis. Its matching only uses the chosen lines/shifts, so it can differ from the full week's plan |

## Data model

Master data changes rarely; weekly data changes every week. `demands.json` and
`availabilities.json` are objects keyed by ISO week (`{"2027-W5": [...], ...}`).
To prepare a new week, copy the previous week's block in both files, change the
key and edit what changes.

### lines.json (master)
```json
{"id": "L3", "name": "Line 3", "restricted_group": {"id": "RG1", "max_consecutive_weeks": 2, "min_rest_weeks": 2}}
```
- `restricted_group` is optional (absent = no restriction). Weeks worked on **any** line of the same group (any shift, any role) count together: after `max_consecutive_weeks` in a row in the group, the operator must stay off all its lines for at least `min_rest_weeks`. All lines of a group must declare the same values; `load_lines` validates this.

### operators.json (master)
```json
{"id": "OP1", "name": "Marie Curie", "lines": {"L3": "qualified", "L4": "qualified"}}
```
- Ids are `OP<n>` with no leading zeros.
- `lines` is the operator's training: line id -> `"specialist"` or `"qualified"`. A line not listed can only be covered as `"assistant"` (no training, there to help or learn).
- Sample names are famous historical figures (no living people).

### demands.json (weekly)
```json
{"2027-W5": [{"line": "L1", "shifts": [{"name": "Morning", "staff": {"specialist": 1, "qualified": 3, "assistant": 1}}]}]}
```
- Shifts the line runs that week (open-ended list) and the exact number of operators of each role each shift needs. A line not listed does not run that week.
- For now only three shifts are used: `Morning`, `Afternoon`, `Night` (no weekend shift, by decision). The format still allows adding more later.

### availabilities.json (weekly)
```json
{"2027-W5": [{"operator": "OP1", "shifts": ["Morning", "Night"]}]}
```
- Shifts the operator can cover that week. All are treated equally (no regular/volunteer distinction, by decision). Empty list or missing operator = not available (holidays, sick leave...).

### history/<period>.json
```json
{"period": "2027-W1", "assignments": [{"operator": "OP33", "line": "L1", "shift": "Morning", "role": "specialist"}]}
```
- One file per week, written by the solver (or edited by hand). Only weeks before the planned one are read.
- Stores the `role`, so later training changes in `operators.json` do not alter the past.
- Periods are ISO weeks as strings `YYYY-W<n>` with no leading zero (`2027-W5`, `2027-W12`). They do **not** sort chronologically as text, so always sort with `sort_iso_weeks` (`library/utils.py`). Never do integer arithmetic on them; convert with `iso_week_to_date` (some years have 53 ISO weeks, e.g. 2026).
- Only ids are stored; names and training come from `operators.json`.

## Sample data (`data/`)

- The simulated data lives directly in `data/` and is committed. Planning with `main.py` or `app.py` writes new history files there; do not commit them unless the user asks.
- `data/backup/` keeps the original `source/` and `history/`. To restore them: delete `data/source` and `data/history` and copy them back from `data/backup/`. If the original data ever changes on purpose, update the backup too.
- 5 lines, 65 operators. L3 and L5 form restricted group RG1.
- History: 2027-W1 to 2027-W4 (47 positions each), with their demands and availabilities.
- Weeks to plan: 2027-W5 to 2027-W8 (48 positions each, identical copies for now; two absences: OP8, OP27). They have been checked to be feasible when planned in sequence after the history.
- Sample data must stay **feasible**: whenever master data, weekly data or rules change, check (e.g. with a quick matching script) that every week can be fully covered and that the history complies with all rules, using each week's own demand and availability (coverage, availability, roles, one assignment per operator per week, restricted groups). Restricted groups need a wide enough trained pool to rotate.
- When planning the next week, the solver must take the latest weeks in the history into account for restricted groups (e.g. an operator with two consecutive weeks in RG1 must rest).

## Ideas discussed, not implemented

- Weekend shift (removed for now), fair distribution of nights using history, global night-shift rotation, operators that do not want to coincide, planning several weeks at once. These do not fit a plain bipartite matching; they are future work / limitations to mention in the thesis (a constraint solver such as OR-Tools CP-SAT would handle them).
