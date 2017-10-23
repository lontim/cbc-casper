import casper.utils as utils


class OracleManager:
    """Stores and updates viewables for an estimate for some validators based on a view"""

    def __init__(self, view, validator_set, safety_threshold):
        self.view = view
        self.validator_set = validator_set
        self.safety_threshold = safety_threshold
        self.viewables_for_estimate = dict()

    def make_new_viewables(self):
        # TODO: get rid of this, by god :)
        for message in self.view.messages:
            self.update_viewables(message)

    def update_viewables(self, new_message):
        """Whenever a new_message is recived, updates the viewables"""
        self._track_new_viewables(new_message)
        # removed all old viewables that validators have seen
        self._remove_outdated_viewables(new_message.sender)

    def _track_new_viewables(self, new_message):
        # for each estimate we are keeping track of
        for estimate in self.viewables_for_estimate:
            # if this new message conflicts with the estimate, could be a free block
            if utils.are_conflicting_estimates(estimate, new_message):
                # make it a viewable for each validator
                for validator in self.validator_set:
                    if validator == new_message.sender: # can't have a viewable for yourself
                        continue

                    # only b/c we might not add the message in "regular" order

                    if self._validator_has_seen_message(validator, new_message):
                        continue

                    viewables = self.viewables_for_estimate[estimate][validator]

                    if new_message.sender not in viewables:
                        self.viewables_for_estimate[estimate][validator][new_message.sender] = \
                                                                                    new_message

                    last_viewable = viewables[new_message.sender]

                    if last_viewable.sequence_number < new_message.sequence_number:
                        self.viewables_for_estimate[estimate][validator][new_message.sender] = \
                                                                                    new_message



    def _remove_outdated_viewables(self, validator):
        # delete old viewables that are outdated, for each estimate
        for estimate in self.viewables_for_estimate:
            # keep track of outdated viewables (can't remove mid-iteration)
            to_remove = set()
            # for each of these viewables
            for val_with_viewable in self.viewables_for_estimate[estimate][validator]:
                viewable = self.viewables_for_estimate[estimate][validator][val_with_viewable]

                if self._validator_has_seen_message(validator, viewable):
                    to_remove.add(val_with_viewable)

            # remove all the outdated viewables
            for val_with_viewable in to_remove:
                del self.viewables_for_estimate[estimate][validator][val_with_viewable]

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


    def _remove_outdated_estimates(self, finalized_estimate):
        # no longer need to keep track of estimates that are a) safe, or b) def not safe
        to_remove = set()

        for estimate in self.viewables_for_estimate:
            if utils.are_conflicting_estimates(finalized_estimate, estimate):
                to_remove.add(estimate)

        for estimate in to_remove:
            del self.viewables_for_estimate[estimate]

        del self.viewables_for_estimate[finalized_estimate]

    def check_safety(self, estimate, oracle_class):
        """Returns if safety on an estimate using the oracle_class is above the safety threshold"""
        # NOTE: Assumes that the viewables are up-to-date!

        if estimate not in self.viewables_for_estimate:
            self.viewables_for_estimate[estimate] = {v: dict() for v in self.validator_set}
            self.make_new_viewables()


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
