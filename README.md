# ShiftPlanner

Automatic allocation of factory staff to production lines and shifts, using [Google OR-Tools](https://developers.google.com/optimization).

## Structure

```
library/        Project functions (models, JSON loading, solver)
tests/          Unit tests (pytest); fixtures/ holds test JSON files
data/source/    Master data: lines.json, operators.json
  weeks/<period>/  Weekly data: demand.json, availability.json
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
