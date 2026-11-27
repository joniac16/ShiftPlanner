"""Unit test for library.loader.load_operators.

Dummy data: data/source/operators.json
  OP1  specialist on L1, qualified on L2
  OP2  qualified on L1
  OP3  no training (can only be an assistant)
"""

from pathlib import Path

from library.loader import load_operators
from library.models import Operator

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {
    "OP1": Operator(id="OP1", name="Marie Curie", lines={"L1": "specialist", "L2": "qualified"}),
    "OP2": Operator(id="OP2", name="Isaac Newton", lines={"L1": "qualified"}),
    "OP3": Operator(id="OP3", name="Ada Lovelace", lines={}),
}


def test_load_operators():
    result = load_operators(DATA_DIR)

    print("\nResult of load_operators:")
    for operator_id, operator in result.items():
        print(f"  {operator_id}: {operator}")

    assert result == EXPECTED
