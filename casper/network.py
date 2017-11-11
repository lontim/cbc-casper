"""The network module .... """
import random as r
import queue as Q
from casper.blockchain.blockchain_protocol import BlockchainProtocol


class Network:
    """Simulates a network that allows for message passing between validators."""
    def __init__(self, validator_set, protocol=BlockchainProtocol):
        self.validator_set = validator_set
        self.global_view = protocol.View(set())
        self.message_queue = Q.PriorityQueue()
        self.current_time = 0


    def send(self, new_message, validator):
        """Adds a message the queue to send to a validator"""
        self.global_view.add_messages(set([new_message]))
        message_tuple = (self.current_time + r.randint(0, 1) + r.random(), new_message, validator)
        print(message_tuple)

        self.message_queue.put(message_tuple)


    def step_forward(self, time_delta):
        self.current_time += time_delta
        return self.do_current_actions()

    def do_current_actions(self):
        actions_taken = []

        if self.message_queue.empty():
            return actions_taken

        time, message, reciever = self.message_queue.get()
        while time < self.current_time:
            assert reciever in self.validator_set, "...expected reciever to be a known validator"
            assert message.header in self.global_view.justified_messages, ("...only propagate "
                                                                           "from global view")
            reciever.receive_messages({message})

            actions_taken.append((message, reciever))

            if self.message_queue.empty():
                return actions_taken

            time, message, reciever = self.message_queue.get()

        return actions_taken

    def get_message_from_validator(self, validator):
        """Get a message from a validator."""
        assert validator in self.validator_set, "...expected a known validator"

        new_message = validator.make_new_message()
        self.global_view.add_messages(set([new_message]))

        return new_message

    def view_initialization(self, view):
        """
        Initalizes all validators with all messages in some view.
        NOTE: This method is not currently tested or called anywhere in repo
        """
        self.global_view = view.messages

        latest = view.latest_messages

        for validator in latest:
            validator.receive_messages(set([latest[validator]]))

    def random_initialization(self):
        """Generates starting messages for all validators with None as an estiamte."""
        for validator in self.validator_set:
            self.get_message_from_validator(validator)
