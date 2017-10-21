import casper.utils as utils

class OracleManager:
    """Stores and updates viewables for an estimate for some validators based on a view"""

    def __init__(self, view, validator_set, safety_threshold):
        self.view = view
        self.validator_set = validator_set
        self.safety_threshold = safety_threshold
        self.viewables_for_estimate = dict()
        self.last_checked_messages = dict()

    def update_viewables(self):
        """For each estimate being tracked, finds new and removes old viewables based on view"""
        # finds all new viewables, for each validator, for each estimate we are keeping track of
        self._track_new_viewables()
        # removed all old viewables that validators have seen
        self._remove_outdated_viewables()
        # for efficiency, updates the last messages we have checked for viewables for each estimate
        self._update_last_checked_messages()


    def _track_new_viewables(self):
        # for each estimate we are keeping track of
        for estimate in self.viewables_for_estimate:
            # get newest messages that are conflicting from each validator (there may be none)
            newest_conflicting_messages = self._get_newest_conflicting_messages(estimate)
            # for each of these newly conflicting messages
            for conflicting_message in newest_conflicting_messages:
                # try to make it a viewable for each validator
                for validator in self.validator_set:
                    msg_sender = conflicting_message.sender
                    # can't be a viewable for a validator who created
                    if msg_sender == validator:
                        continue
                    # can only be a viewable if a validator has not seen it!
                    if not self._validator_has_seen_message(validator, conflicting_message):
                        self.viewables_for_estimate[estimate][validator][msg_sender] = \
                                                                    conflicting_message

    def _remove_outdated_viewables(self):
        # delete old viewables that are outdated, for each estimate
        for estimate in self.viewables_for_estimate:
            # for each validator we have seen a message from (only way to see viewables!)
            for validator in self.view.latest_messages:
                # keep track of outdated viewables (can't remove mid-iteration)
                to_remove = set()
                # for each of these viewables
                for val_with_viewable in self.viewables_for_estimate[estimate][validator]:
                    viewable = self.viewables_for_estimate[estimate][validator][val_with_viewable]
                    if viewable:
                        # if the validator has seen the viewable, then we can remove it
                        if self._validator_has_seen_message(validator, viewable):
                            to_remove.add(val_with_viewable)

                # remove all the outdated viewables
                for val_with_viewable in to_remove:
                    del self.viewables_for_estimate[estimate][validator][val_with_viewable]


    def _update_last_checked_messages(self):
        for estimate in self.viewables_for_estimate:
            for validator in self.view.latest_messages:
                self.last_checked_messages[estimate][validator] = \
                                self.view.latest_messages[validator]

    def _validator_has_seen_message(self, validator, message):

        if validator not in self.view.latest_messages:
            return False

        latest_msgs_val_saw = self.view.latest_messages[validator].justification.latest_messages

        if message.sender not in latest_msgs_val_saw:
            return False

        if message.sequence_number > latest_msgs_val_saw[message.sender].sequence_number:
            return False

        # just for testing, not actually allowed in the real world :)
        assert message in validator.view.messages, "...should have seen message!"
        return True


    def _get_newest_conflicting_messages(self, estimate):
        # dict from validator (not all) => newest conflicting message with estimate
        # NOTE: consider the most newest message as all oracles are assumed to be side effects free
        newest_conflicting_messages = set()

        # for each validator we have seen messages from
        for validator in self.view.latest_messages:

            # if we previous checked some of their messages
            if validator in self.last_checked_messages[estimate]:
                # then the last_checked_sequence_num is the message we checked
                last_checked_seq = self.last_checked_messages[estimate][validator].sequence_number
            else:
                # otherwise, we've never checked something from them before
                # TODO: low hanging fruid for optimization here:
                # set the last_checked_sequence_num to be the oldest message from this validator
                # in the justification of the latest messages from all validators
                last_checked_seq = -1

            # start at their most recent message, and go to the last message we checked
            tip = self.view.latest_messages[validator]
            while tip and tip.sequence_number > last_checked_seq:
                # if the message conflicts, stop looking!
                if utils.are_conflicting_estimates(estimate, tip):
                    newest_conflicting_messages.add(tip)
                    break
                if validator not in tip.justification.latest_messages:
                    break
                tip = tip.justification.latest_messages[validator]

        return newest_conflicting_messages



    def _remove_outdated_estimates(self, finalized_estimate):
        # no longer need to keep track of estimates that are a) safe, or b) def not safe
        to_remove = set()

        for estimate in self.viewables_for_estimate:
            if utils.are_conflicting_estimates(finalized_estimate, estimate):
                to_remove.add(estimate)

        for estimate in to_remove:
            del self.last_checked_messages[estimate]
            del self.viewables_for_estimate[estimate]

        del self.viewables_for_estimate[finalized_estimate]


    def check_safety(self, estimate, oracle_class):
        """Returns if safety on an estimate using the oracle_class is above the safety threshold"""
        if estimate not in self.viewables_for_estimate:
            self.last_checked_messages[estimate] = dict()
            self.viewables_for_estimate[estimate] = {v: dict() for v in self.validator_set}

        self.update_viewables()

        # create a new safety oracle
        oracle = oracle_class(
            estimate,
            self.view,
            self.validator_set,
            self.viewables_for_estimate[estimate]
        )
        fault_tolerance, _ = oracle.check_estimate_safety()

        if fault_tolerance > self.safety_threshold:
            # we no longer have to track estimates that cannot be safe
            self._remove_outdated_estimates(estimate)
            return True

        return False
