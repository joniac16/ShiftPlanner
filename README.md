# ShiftPlanner

Automatic allocation of factory staff to production lines and shifts, using [Google OR-Tools](https://developers.google.com/optimization).

## Structure

```
library/        Project functions (models, JSON loading, solver)
tests/          Unit tests (pytest); fixtures/ holds test JSON files
data/source/    Input data: operators.json, lines.json, history.json
data/output/    Generated allocations (JSON)
main.py         Entry point
```

## Usage

```bash
pip install -r requirements.txt
python main.py
pytest
```
