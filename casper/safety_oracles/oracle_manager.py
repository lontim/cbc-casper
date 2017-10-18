from casper.safety_oracles.clique_oracle import CliqueOracle
from casper.safety_oracles.turan_oracle import TuranOracle
from casper.safety_oracles.adversary_oracle import AdversaryOracle

import casper.utils as utils

class OracleManager:

    def __init__(self, view, validator_set, safety_threshold):
        self.validator_set = validator_set
        self.view = view
        self.safety_threshold = safety_threshold
        self.viewables_for_estimate = dict()
        self.last_checked_messages = dict()


    def update_viewables():
        new_messages = self.get_new_messages()

        # for each estimate we are keeping track of
        for estimate in self.viewables_for_estimate:
            # for each new message
            for message in new_messages:
                # if this new message could be a free message
                if utils.are_conflicting_estimates(estimate, message):
                    # then for all validators it could be a free block for
                    for validator in self.validator_set:
                        if validator != message.sender: # can't make a free block for yourself!
                            if message.sender not in view.latest_messages[validator].justification.latest_messages:
                                seq_number = -1
                            else:
                                seq_number = view.latest_messages[validator].justification.latest_messages[message.sender].sequence_number

                            # if it is a free block
                            if message.sequence_number > seq_number:
                                # NOTE: preferably, would not do this for all new messages - rather just latest free block?
                                # Maybe can do messages by validator - and stop as soon as we find a viewable!

                                # then make it viewable
                                self.viewables_for_estimate[estimate][validator][message.sender] = message

            # now remove all outdated viewables
            for validator in self.validator_set:
                to_remove = set()
                # for the viewables for some validator
                for v in self.viewables_for_estimate[estimate][validator]:
                    latest_viewable = self.viewables_for_estimate[estimate][validator][v]

                    if v not in self.view.latest_message[validator].justification.latest_message:
                        latest_seen_seq = -1
                    else:
                        latest_seen_seq = self.view.latest_message[validator].justification.latest_message[v].sequence_number

                    # if the latest message they have seen is later than this viewable, then it's no longer a viewable
                    if latest_viewable.sequence_number <= latest_seen_seq:
                        to_remove.add(v)

                # remove these no-longer-valid-viewables
                for v in to_remove:
                    del self.viewables_for_estimate[estimate][validator][v]

        # update our latest checked messages
        for v in view.latest_messages:
            self.last_checked_for_edges[v] = view.latest_messages[v]

    def get_new_messages(self):
        new_messages = set()
        for v in view.latest_messages:

            if v not in self.last_checked_for_edges:
                last_checked_sequence_num = -1
            else:
                last_checked_sequence_num = self.last_checked_messages[v].sequence_number

            tip = view.latest_messages[v]
            while tip and tip.sequence_number > last_checked_sequence_num:
                new_messages.add(tip)
                tip = tip.justification.latest_messages[v]

        return new_messages


    def check_safety(self, estimate):
        if estimate not in self.viewables_for_estimate:
            self.viewables_for_estimate[estimate] = {v: dict() for v in self.validator_set}

        self.update_viewables()

        oracle = AdversaryOracle(estimate, self.viewables_for_estimate[estimate])
        fault_tolerance, _ = oracle.check_estimate_safety()

        if fault_tolerance > self.safety_threshold:
            self.remove_outdated_estimates(estimate)
            return True
        else:
            return False



    def remove_outdated_estimates(self, finalized_estimate):
        # no longer need to keep track of estimates that are a) safe, or b) def not safe
        to_remove = set()

        for estimate in self.viewables_for_estimate:
            if estimate.height < finalized_estimate.height:
                to_remove.add(estimate)
            if utils.are_conflicting_estimates(finalized_estimate, estimate):
                to_remove.add(estimate)

        for estimate in to_remove:
            del self.viewables_for_estimate[estimate]
