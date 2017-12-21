import pytest

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from casper.protocols.binary.binary_protocol import BinaryProtocol
from casper.protocols.integer.integer_protocol import IntegerProtocol
from casper.protocols.order.order_protocol import OrderProtocol


@pytest.mark.parametrize(
    'protocol',
    (
        OrderProtocol,
        BlockchainProtocol,
        BinaryProtocol,
        IntegerProtocol
    )
)
def test_class_properties_defined(protocol):
    protocol.View
    protocol.Message
    protocol.PlotTool

    assert callable(protocol.initial_message)
