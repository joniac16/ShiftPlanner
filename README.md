# ShiftPlanner

Automatic allocation of factory staff to production lines and shifts, using [Google OR-Tools](https://developers.google.com/optimization).

## Structure

```
library/        Project functions (models, JSON loading, solver)
tests/          Unit tests (pytest): unit_testing/<function>/ with test file and data
data/source/    lines.json, operators.json (master data);
                demands.json, availabilities.json (weekly data, keyed by ISO week)
data/output/    Allocation proposals, one JSON per week
data/history/   Approved allocations, one JSON per week
main.py         Entry point
```

## Usage

```bash
pip install -r requirements.txt
python main.py
pytest
```
