import pytest

from state_languages.blockchain_test_lang import BlockchainTestLang
from state_languages.integer_test_lang import IntegerTestLang
from state_languages.binary_test_lang import BinaryTestLang

@pytest.fixture
def empty_just():
    return {}

@pytest.fixture
def example_function():
    def example_func():
        return
    return example_func


@pytest.fixture
def binary_lang(report, test_weight):
    return BinaryTestLang(test_weight, report)


@pytest.fixture
def binary_lang_creator(report):
    def create_binary_lang(test_weight):
        return BinaryTestLang(test_weight, report)
    return create_binary_lang


@pytest.fixture
def binary_lang_runner(report):
    def run_binary_lang(test_string, weights):
        BinaryTestLang(weights, report).parse(test_string)
    return run_binary_lang


@pytest.fixture
def blockchain_lang(report, test_weight):
    return BlockchainTestLang(test_weight, report)


@pytest.fixture
def blockchain_lang_creator(report):
    def create_blockchain_lang(test_weight):
        return BlockchainTestLang(test_weight, report)
    return create_blockchain_lang


@pytest.fixture
def blockchain_lang_runner(report):
    def run_blockchain_lang(test_string, weights):
        BlockchainTestLang(weights, report).parse(test_string)
    return run_blockchain_lang


@pytest.fixture
def integer_lang(report, test_weight):
    return IntegerTestLang(test_weight, report)


@pytest.fixture
def integer_lang_creator(report):
    def create_integer_lang(test_weight):
        return BlockchainTestLang(test_weight, report)
    return create_integer_lang


@pytest.fixture
def integer_lang_runner(report):
    def run_integer_lang(test_string, weights):
        IntegerTestLang(weights, report).parse(test_string)
    return run_integer_lang
