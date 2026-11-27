"""Plan several weeks in a row: the loop used by main.py and by the front end (app.py).

`solver.solve` plans one week; `plan_weeks` chains several, so that each week
sees the ones planned before it (restricted groups), and saves them all at
the end, only if every week could be planned.
"""

from pathlib import Path

from library.loader import DEFAULT_DATA_DIR, DataError, load_history, load_planning_input
from library.models import MatchWeights, PlanningResult
from library.solver import solve, validate_week
from library.utils import iso_week_to_date, make_iso_week, next_iso_week
from library.writer import save_week


def plan_weeks(
    start_year: int,
    start_week: int,
    end_year: int,
    end_week: int,
    data_dir: Path | str = DEFAULT_DATA_DIR,
    weights: MatchWeights | None = None,
    maximize_matches: bool = True,
    overwrite: bool = False,
) -> list[PlanningResult]:
    """Plan every week from (start_year, start_week) to (end_year, end_week), both included.

    - data_dir: data folder (source/ and history/).
    - weights: edge weights (`MatchWeights`); defaults if None.
    - maximize_matches: True -> as many slots covered as possible, then highest
      weight; False -> highest weight only.
    - overwrite: allow replacing weeks of the range that are already in the history.

    How it works:
      1. The whole history is loaded into memory (with overwrite, the weeks of
         the range are dropped from it, so the old versions are not used).
      2. Week by week: the week's data is loaded, its history is replaced by
         the in-memory one (weeks before it), it is solved and validated, and
         its allocation is added to the in-memory history, so the next week
         sees it.
      3. Only if every week was planned, all of them are saved to the history
         with `save_week`.
    If something fails, DataError is raised saying which week, and no file is
    written. Returns one PlanningResult per week, in order.
    """
    try:
        start = make_iso_week(start_year, start_week)
        end = make_iso_week(end_year, end_week)
    except ValueError as error:
        raise DataError(f"Invalid week: {error}") from None
    if iso_week_to_date(start) > iso_week_to_date(end):
        raise DataError(f"The start week {start} is after the end week {end}")

    weeks = [start]
    while weeks[-1] != end:
        weeks.append(next_iso_week(weeks[-1]))

    history = load_history(data_dir)
    already_saved = [week.period for week in history if week.period in weeks]
    if already_saved and not overwrite:
        raise DataError(f"Weeks already in the history: {', '.join(already_saved)}; use overwrite=True to replace them")
    history = [week for week in history if week.period not in weeks]

    results: list[PlanningResult] = []
    for week in weeks:
        try:
            data = load_planning_input(week, data_dir)
            monday = iso_week_to_date(week)
            data.history = sorted(
                (w for w in history if iso_week_to_date(w.period) < monday),
                key=lambda w: iso_week_to_date(w.period),
            )
            result = solve(data, weights, maximize_matches)
            validate_week(result.allocation, data)
        except DataError as error:
            raise DataError(f"Error planning {week} (nothing was saved): {error}") from error
        history.append(result.allocation)
        results.append(result)

    for result in results:
        save_week(result.allocation, data_dir, overwrite=overwrite)

    return results
