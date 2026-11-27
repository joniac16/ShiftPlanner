# ShiftPlanner

Automatic allocation of factory staff to production lines and shifts, using [Google OR-Tools](https://developers.google.com/optimization).

## Structure

```
library/        Project functions (models, JSON loading, solver)
test/           Unit tests (pytest): <module>/<function>/ with test file and dummy data
sample_data/    Sample (simulated) data:
  source/       lines.json, operators.json (master data);
                demands.json, availabilities.json (weekly data, keyed by ISO week)
  history/      Planned weeks, one JSON per week (written by the solver, read back for later weeks)
data/           Working copy, empty in the repository and ignored by git. The first time
                main.py or app.py runs, sample_data/ is copied into it; all planning
                happens there. Delete its contents to start again from the samples.
main.py         Command line entry point (plan_weeks)
app.py          Web front end (Streamlit)
```

## Usage

```bash
pip install -r requirements.txt
```

Plan a range of weeks and save them to `data/history/`:

```bash
python main.py --start-year 2027 --start-week 5 --end-year 2027 --end-week 8
```

Options: `--data-dir`, `--maximize matches|weight`, `--overwrite`, and one option per edge weight (see `python main.py --help`).

Or use the web front end (Plan, Schedule, Data and Graph screens):

```bash
streamlit run app.py
```

Run the tests:

```bash
python -m pytest -v -s
```
