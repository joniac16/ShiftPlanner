"""Writing of the JSON files: what comes out of the algorithm.

`loader.py` reads the data into the algorithm; this module writes its
results back. Every function takes the data folder as a parameter (`data` by
default), so tests can use their own folder:

    <data_dir>/history/<period>.json
"""

import json
from pathlib import Path

from library.loader import DEFAULT_DATA_DIR, DataError, load_planning_input
from library.models import WeekAllocation
from library.solver import validate_week
from library.utils import iso_week_to_date


def save_week(
    allocation: WeekAllocation,
    data_dir: Path | str = DEFAULT_DATA_DIR,
    overwrite: bool = False,
) -> Path:
    """Validate a week's allocation and save it to history/<period>.json.

    - The allocation is checked with `validate_week` against that week's data
      (and the history before it). If it is not valid, DataError is raised
      and nothing is written.
    - If the week is already in the history, DataError is raised unless
      overwrite=True.
    - If later weeks are already in the history, a warning is printed (they
      were planned with the previous version of this week) and the week is
      saved anyway.

    The file has the same format as the rest of the history: one assignment
    per line. Returns the path of the file written.
    """
    data_dir = Path(data_dir)
    period = allocation.period

    validate_week(allocation, load_planning_input(period, data_dir))

    folder = data_dir / "history"
    path = folder / f"{period}.json"
    if path.exists() and not overwrite:
        raise DataError(f"Week {period} is already in the history ({path}); use overwrite=True to replace it")

    start = iso_week_to_date(period)
    later = sorted(p.stem for p in folder.glob("*.json") if iso_week_to_date(p.stem) > start)
    if later:
        print(f"Warning: saving {period}, but later weeks are already in the history: {', '.join(later)}. "
              f"They were planned with the previous version of {period}.")

    rows = ",\n".join("    " + json.dumps(a.__dict__) for a in allocation.assignments)
    body = f"\n{rows}\n  " if rows else ""
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(f'{{\n  "period": "{period}",\n  "assignments": [{body}]\n}}\n', encoding="utf-8")
    return path
