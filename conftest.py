import random as r
import pytest

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.protocols.integer.integer_protocol import IntegerProtocol
from casper.protocols.binary.binary_protocol import BinaryProtocol
from casper.protocols.order.order_protocol import OrderProtocol

from casper.networks import (
    ConstantDelayNetwork,
    NoDelayNetwork
)

from simulations.utils import generate_random_gaussian_validator_set


PROTOCOLS = [BlockchainProtocol, BinaryProtocol, IntegerProtocol, OrderProtocol]


def pytest_addoption(parser):
    parser.addoption("--report", action="store_true", default=False,
                     help="plot TestLangCBC tests")


def random_gaussian_validator_set_from_protocol(protocol=BlockchainProtocol):
    return generate_random_gaussian_validator_set(protocol)


@pytest.fixture(autouse=True)
def reset_blockchain_protocol(request):
    BlockchainProtocol.genesis_block = None


@pytest.fixture
def report(request):
    return request.config.getoption("--report")


@pytest.fixture
def test_weight():
    return {i: 5 - i for i in range(5)}


@pytest.fixture
def generate_validator_set():
    return random_gaussian_validator_set_from_protocol


@pytest.fixture(params=PROTOCOLS)
def protocol(request):
    return request.param


@pytest.fixture
def validator_set(protocol):
    return random_gaussian_validator_set_from_protocol(protocol)


@pytest.fixture
def validator(validator_set):
    return r.choice(list(validator_set.validators))


@pytest.fixture
def to_from_validators(validator_set):
    return r.sample(
        validator_set.validators,
        2
    )


@pytest.fixture
def to_validator(to_from_validators):
    return to_from_validators[0]


@pytest.fixture
def from_validator(to_from_validators):
    return to_from_validators[1]


@pytest.fixture
def network(protocol, validator_set):
    return NoDelayNetwork(validator_set, protocol)


@pytest.fixture
def no_delay_network(protocol, validator_set):
    return NoDelayNetwork(validator_set, protocol)


@pytest.fixture
def constant_delay_network(protocol, validator_set):
    return ConstantDelayNetwork(validator_set, protocol)


@pytest.fixture
def global_view(network):
    return network.global_view
