import random as r
import pytest
from casper.safety_oracles.oracle_manager import OracleManager
from casper.validator_set import ValidatorSet
from casper.view import View
import casper.utils as utils

DECREASING_WEIGHT = {0: 9.3, 1: 8.2, 2: 7.1, 3: 6, 4: 5}

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



def test_tracks_estimates_without_safety(test_lang_runner):
    # If validator checks safety on A, B, and C, and does not find it, stores viewables for them
    test_string = "B0-A S1-A B1-B S2-B B2-C U2-A U2-B U2-C"
    test_lang = test_lang_runner(test_string, DECREASING_WEIGHT)

    validator = test_lang.validator_set.get_validator_by_name(2)
    # As checked safety on all blocks and didn't find it, should have cached all work
    for block in test_lang.blocks.values():
        assert block in validator.oracle_manager.viewables_for_estimate


def test_only_tracks_currest_estimates(test_lang_runner):
    # If a validator checks safety, does not find it, then later does, should stop tracking it
    # Should also stop tracking all estimates that implicity finalized by it
    test_string = "B0-A S1-A B1-B S2-B B2-C U2-A U2-B U2-C RR2-D RR3-E RR2-F C2-C"
    test_lang = test_lang_runner(test_string, DECREASING_WEIGHT)

    validator = test_lang.validator_set.get_validator_by_name(2)
    assert test_lang.blocks['A'] not in validator.oracle_manager.viewables_for_estimate
    assert test_lang.blocks['B'] not in validator.oracle_manager.viewables_for_estimate
    assert test_lang.blocks['C'] not in validator.oracle_manager.viewables_for_estimate


def test_sees_all_viewables_for_estimates(test_lang_runner):
    # If there are viewables from some estimate, make sure the manager sees these viewables
    test_string = "B0-A S1-A B1-B S2-B B2-C B3-D S2-D U2-D"
    test_lang = test_lang_runner(test_string, DECREASING_WEIGHT)

    # for the estimate D, in validator 2's view, val 3 should have A, B, C as viewables
    vals = test_lang.validator_set.sorted_by_name()
    viewables = vals[2].oracle_manager.viewables_for_estimate[test_lang.blocks['D']]
    assert test_lang.blocks['A'] == viewables[vals[3]][vals[0]]
    assert test_lang.blocks['B'] == viewables[vals[3]][vals[1]]
    assert test_lang.blocks['C'] == viewables[vals[3]][vals[2]]
    assert len(viewables[vals[3]]) == 3

def test_picks_most_recent_viewables(test_lang_runner):
    # If there are mulitple viewables to pick from, picks the most recent one
    test_string = "B0-A B0-B S1-B B1-C S2-C B2-D B3-E S2-E U2-E"
    test_lang = test_lang_runner(test_string, DECREASING_WEIGHT)

    vals = test_lang.validator_set.sorted_by_name()
    viewables = vals[2].oracle_manager.viewables_for_estimate[test_lang.blocks['E']]
    assert test_lang.blocks['B'] == viewables[vals[3]][vals[0]] # should not be block A
    assert len(viewables[vals[3]]) == 3


def test_only_finds_valid_viewables(test_lang_runner):
    # Make sure that if a block is not a viewable, it does not get seen as one
    test_string = "RR0-T B0-A S1-A B1-B S2-B B2-C B3-D S3-C B3-E S2-E U2-A"
    # Note: we have a round of round robin first to make sure val all see starting blocks
    test_lang = test_lang_runner(test_string, DECREASING_WEIGHT)

    vals = test_lang.validator_set.sorted_by_name()
    viewables = vals[2].oracle_manager.viewables_for_estimate[test_lang.blocks['A']]
    assert vals[1] not in viewables[vals[0]]
    assert vals[2] not in viewables[vals[0]]
    assert len(viewables[vals[0]]) == 1
    assert test_lang.blocks['D'] == viewables[vals[0]][vals[3]] # D is free, E is not
