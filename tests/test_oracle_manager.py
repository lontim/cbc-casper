import random as r
import pytest
from casper.safety_oracles.oracle_manager import OracleManager
from casper.validator_set import ValidatorSet
from casper.view import View

@pytest.mark.parametrize(
    'weights',
    [
        ({i: i for i in range(10)}),
        ({i: r.random() for i in range(10)}),
    ]
)
def test_oracle_manager_initalization(weights):
    validator_set = ValidatorSet(weights)
    view = View()
    oracle_manager = OracleManager(view, validator_set, 0)
    assert oracle_manager.validator_set == validator_set
    assert oracle_manager.view == view
    assert not any(oracle_manager.viewables_for_estimate)
    assert not any(oracle_manager.last_checked_messages)
