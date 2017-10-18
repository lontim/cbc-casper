"""The adversary oracle module ... """
from casper.safety_oracles.adversary_models.model_bet import ModelBet
from casper.safety_oracles.adversary_models.adversary import Adversary
from casper.safety_oracles.abstract_oracle import AbstractOracle
import casper.utils as utils


class AdversaryOracle(AbstractOracle):
    """Runs an lower bound adversary to check safety on some estimate."""

    # We say candidate_estimate is 0, other is 1
    CAN_ESTIMATE = 0
    ADV_ESTIMATE = 1

    def __init__(self, candidate_estimate, view, validator_set, viewables):
        if candidate_estimate is None:
            raise Exception("cannot decide if safe without an estimate")

        self.candidate_estimate = candidate_estimate
        self.view = view
        self.validator_set = validator_set
        self.viewables = viewables


    def get_recent_messages_and_viewables(self):
        """Converts some viewables to binary version."""

        recent_messages = dict()
        binary_viewables = dict()

        for validator in self.validator_set:
            # ... if nothing is seen from validator, assume the worst ...
            if validator not in self.view.latest_messages:
                recent_messages[validator] = ModelBet(AdversaryOracle.ADV_ESTIMATE, validator)
                binary_viewables[validator] = dict()

            # ... or if their most recent messages conflicts w/ estimate,
            # again working with adversary.
            elif utils.are_conflicting_estimates(self.candidate_estimate,
                                                 self.view.latest_messages[validator]):
                recent_messages[validator] = ModelBet(AdversaryOracle.ADV_ESTIMATE, validator)
                binary_viewables[validator] = dict()

            else:
                # Sanity check!
                assert not utils.are_conflicting_estimates(self.candidate_estimate, self.view.latest_messages[validator])

                recent_messages[validator] = ModelBet(AdversaryOracle.CAN_ESTIMATE, validator)
                viewables[validator] = dict()

                for val2 in self.validator_set:

                    if val2 in self.viewables[validator]:
                        viewables[validator][val2] = ModelBet(AdversaryOracle.ADV_ESTIMATE, val2)
                    else:
                        viewables[validator][val2] = ModelBet(AdversaryOracle.CAN_ESTIMATE, val2)


        return recent_messages, viewables

    def check_estimate_safety(self):
        """Check the safety of the estimate."""

        recent_messages, viewables = self.get_recent_messages_and_viewables()

        adversary = Adversary(self.CAN_ESTIMATE, recent_messages, viewables, self.validator_set)

        attack_success, _, _ = adversary.ideal_network_attack()

        if not attack_success:
            # Because the adversary tells us nothing about validators that need to equivocate,
            # assume the worst.
            return min(self.validator_set.validator_weights()), 1
        else:
            return 0, 0
