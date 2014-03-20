from friendsecure.protocol import MessageProtocol
from mock import MagicMock
import json


def test_stringReceived():
    proto = MessageProtocol()
    # *SIGH*
    class C(object):
        def __init__(self, name, val):
            setattr(self, name, val)

    node = C('message_received', MagicMock())
    factory = C('node', node)
    setattr(proto, 'factory', factory)
    msg = {
        'type': 'message',
        'message': 'hello'
    }
    proto.stringReceived(json.dumps(msg))
    assert 1 == proto.factory.node.message_received.call_count
    assert msg == proto.factory.node.message_received.call_args[0][0]


def test_sendMessage():
    proto = MessageProtocol()

    proto.sendString = MagicMock()
    msg_dict = {
        'type': 'message',
        'message': 'hello'
    }
    proto.sendMessage(msg_dict)
    assert 1 == proto.sendString.call_count
    assert json.dumps(msg_dict) == proto.sendString.call_args[0][0]


def test_error():
    proto = MessageProtocol()
    proto.sendMessage = MagicMock()
    expected_message = {
        'type': 'error',
        'description': 'BANG!'
    }
    proto.error('BANG!')
    assert 1 == proto.sendMessage.call_count
    assert expected_message == proto.sendMessage.call_args[0][0]
