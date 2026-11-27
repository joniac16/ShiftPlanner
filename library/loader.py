"""Reading and writing of the JSON files.

Every function takes the data folder as a parameter (`data` by default), so
tests can use their own dummy data with the same layout:

    <data_dir>/source/lines.json
"""

import json
from pathlib import Path

from library.models import Line, RestrictedGroup

DEFAULT_DATA_DIR = Path("data")


class DataError(ValueError):
    """The data files are malformed or inconsistent."""


def load_lines(data_dir: Path | str = DEFAULT_DATA_DIR) -> dict[str, Line]:
    """Read source/lines.json and return a dict: line id -> Line.

    Raises DataError if a line id is repeated, or if two lines of the same
    restricted group declare different limits.
    """
    path = Path(data_dir) / "source" / "lines.json"
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    lines: dict[str, Line] = {}
    groups: dict[str, RestrictedGroup] = {}

    for item in raw:
        line_id = item["id"]
        if line_id in lines:
            raise DataError(f"Duplicate line id '{line_id}' in {path}")

        group = None
        if "restricted_group" in item:
            group = RestrictedGroup(**item["restricted_group"])
            if group.id in groups and groups[group.id] != group:
                raise DataError(
                    f"Restricted group '{group.id}' has different limits on line {line_id} "
                    f"than on other lines of the group"
                )
            groups[group.id] = group

        lines[line_id] = Line(id=line_id, name=item["name"], restricted_group=group)

    return lines
