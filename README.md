# ShiftPlanner

Automatic allocation of factory staff to production lines and shifts, modelled as a maximum-weight matching in a bipartite graph (operators and slots), solved with [NetworkX](https://networkx.org/).

## Online apps (Streamlit Community Cloud)

| Branch | Environment | App |
|---|---|---|
| `main` | production | <https://shiftplanner-zwrt9xfbaj6xbarynitodx.streamlit.app> |
| `test` | testing | <https://shiftplanner-yyfr3xq9qox3qnm4zkqvyt.streamlit.app> |
| `dev` | development | <https://shiftplanner-nk7dbykj2bjhw5sy6l7vug.streamlit.app> |

Each app runs `app.py` from its branch. Changes flow `dev` -> `test` -> `main`. Weeks planned in an online app are lost when the app restarts.

## Structure

```
library/        Project functions (models, JSON loading, solver)
test/           Unit tests (pytest): <module>/<function>/ with test file and dummy data
data/           Simulated data:
  source/       lines.json, operators.json (master data);
                demands.json, availabilities.json (weekly data, keyed by ISO week)
  history/      Planned weeks, one JSON per week (written by the solver, read back for later weeks)
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

Or use the web front end (screens: Plan assignments, View assignments, View source data):

```bash
streamlit run app.py
```

Run the tests:

```bash
python -m pytest -v -s
```
