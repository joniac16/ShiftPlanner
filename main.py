"""Command line entry point: plan a range of weeks and save them to the history.

Example:
    python main.py --start-year 2027 --start-week 5 --end-year 2027 --end-week 8

All the work is done by `library.planner.plan_weeks`, which a front end can
call directly with the same arguments.
"""

import argparse
import sys
from pathlib import Path

from library.loader import DataError
from library.models import MatchWeights
from library.planner import plan_weeks


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    defaults = MatchWeights()
    parser = argparse.ArgumentParser(description="Plan factory operators into lines and shifts, week by week.")
    parser.add_argument("--start-year", type=int, required=True, help="year of the first week to plan")
    parser.add_argument("--start-week", type=int, required=True, help="ISO week number of the first week")
    parser.add_argument("--end-year", type=int, required=True, help="year of the last week to plan")
    parser.add_argument("--end-week", type=int, required=True, help="ISO week number of the last week")
    parser.add_argument("--data-dir", default="data",
                        help="working data folder with source/ and history/ (default: data)")
    parser.add_argument("--maximize", choices=["matches", "weight"], default="matches",
                        help="matches: cover as many slots as possible, then highest weight (default); "
                             "weight: highest weight only")
    parser.add_argument("--overwrite", action="store_true", help="replace weeks already in the history")

    weights = parser.add_argument_group("weights", "edge weights (higher = preferred)")
    for name, value in defaults.__dict__.items():
        weights.add_argument(f"--{name.replace('_', '-')}", type=float, default=value, help=f"default: {value}")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)
    weights = MatchWeights(**{name: getattr(args, name) for name in MatchWeights().__dict__})

    if not (Path(args.data_dir) / "source").exists():
        print(f"Error: no data in {args.data_dir}/source. Copy the sample data first "
              f"(the contents of sample_data/ into {args.data_dir}/) or use --data-dir.", file=sys.stderr)
        return 1

    try:
        results = plan_weeks(
            args.start_year, args.start_week, args.end_year, args.end_week,
            data_dir=args.data_dir,
            weights=weights,
            maximize_matches=args.maximize == "matches",
            overwrite=args.overwrite,
        )
    except DataError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    for result in results:
        allocation = result.allocation
        print(f"{allocation.period}: {len(allocation.assignments)} assignments, "
              f"{len(result.uncovered_slots)} uncovered slots, "
              f"{len(result.unassigned_operators)} unassigned operators, total weight {result.total_weight}")
        for slot, candidates in result.uncovered_slots.items():
            print(f"    uncovered: {slot} ({candidates} candidate(s))")
    print(f"Saved {len(results)} week(s) to {args.data_dir}/history/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
