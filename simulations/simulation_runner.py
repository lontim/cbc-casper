import sys

from casper.network import Network


class SimulationRunner:
    def __init__(
            self,
            validator_set,
            msg_gen,
            protocol,
            total_rounds,
            report_interval,
            display,
            save,
    ):
        self.validator_set = validator_set
        self.msg_gen = msg_gen
        self.save = save

        self.round = 0
        if total_rounds:
            self.total_rounds = total_rounds
        else:
            self.total_rounds = sys.maxsize

        if report_interval:
            self.report_interval = report_interval
        else:
            self.report_interval = 1

        self.network = Network(validator_set, protocol)
        self.network.random_initialization()

        self.plot_tool = protocol.PlotTool(display, save, self.network.global_view, validator_set)
        self.plot_tool.plot()

    def run(self):
        """ run simulation total_rounds if specified
            otherwise, run indefinitely """
        while self.round < self.total_rounds:
            self.step()

        if self.save:
            self.plot_tool.make_gif()

    def step(self):
        """ run one round of the simulation """
        self.round += 1
        if (self.round % 3 == 0):
            for sender in self.msg_gen(self.validator_set):
                message = sender.my_latest_message()
                self.network.send_to_all_validators(message)

        actions_taken = self.network.step_forward(10)

        affected_validators = {receiver for _, receiver in actions_taken}


        new_messages = self._make_new_messages(affected_validators)
        self._check_for_new_safety(affected_validators)

        self.plot_tool.update(actions_taken, new_messages)
        if self.round % self.report_interval == self.report_interval - 1:
            self.plot_tool.plot()



    def _make_new_messages(self, validators):
        messages = {}
        for validator in validators:
            message = self.network.get_message_from_validator(validator)
            messages[validator] = message

        return messages

    def _check_for_new_safety(self, affected_validators):
        for validator in affected_validators:
            validator.update_safe_estimates()

        self.network.global_view.update_safe_estimates(self.validator_set)
