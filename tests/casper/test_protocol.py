import pytest

def test_class_properties_defined(protocol):
    protocol.View
    protocol.Message
    protocol.PlotTool

    assert callable(protocol.initial_message)
