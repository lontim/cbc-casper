"""The BlockchainView testing module..."""
import pytest

from casper.protocols.blockchain.blockchain_protocol import BlockchainProtocol
from state_languages.blockchain_test_lang import BlockchainTestLang


@pytest.mark.parametrize(
    'test_string, children',
    [
        ('M0-A M0-B S1-A S1-B M1-C', {'A': {'B'}, 'B': {'C'}}),
        ('M0-A M0-B S1-A M1-C', {'A': {'B', 'C'}}),
        ('M0-A M0-B S1-A M1-C S2-A M2-D S3-A M3-E S4-A M4-F', {'A': {'B', 'C', 'D', 'E', 'F'}}),
        ('RR0-A M0-B M0-C SJ1-A M1-D M1-E', {'A': {'B', 'D'}, 'B': {'C'}, 'D': {'E'}}),
    ]
)
def test_update_protocol_specific_view_adds_children(test_string, children, blockchain_lang):
    blockchain_lang.parse(test_string)

    for parent in children:
        block = blockchain_lang.messages[parent]

        for child in children[parent]:
            child_block = blockchain_lang.messages[child]
            assert child_block in blockchain_lang.network.global_view.children[block]

        assert len(children[parent]) == len(blockchain_lang.network.global_view.children[block])



@pytest.mark.skip(reason="test not yet implemented")
def test_add_justified_message():
    pass

@pytest.mark.skip(reason="test not yet implemented")
def test_dont_add_non_justified_message():
    pass

@pytest.mark.skip(reason="test not yet implemented")
def test_resolve_non_justified_message_when_justification_arrives():
    pass
