# ShiftPlanner

Automatic allocation of factory staff to production lines and shifts, using [Google OR-Tools](https://developers.google.com/optimization).

## Structure

```
library/        Project functions (models, JSON loading, solver)
test/           Unit tests (pytest): <module>/<function>/ with test file and dummy data
data/source/    lines.json, operators.json (master data);
                demands.json, availabilities.json (weekly data, keyed by ISO week)
data/history/   Planned weeks, one JSON per week (written by the solver, read back for later weeks)
main.py         Entry point
```

## Usage

```bash
pip install -r requirements.txt
python main.py
pytest
```
