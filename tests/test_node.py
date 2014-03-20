from friendsecure.node import Node
from mock import MagicMock
import json


def test_message_received():
    class Screen(object):
        def __init__(self):
            self.addLine = MagicMock()

    screen = Screen()

    class Peer(object):
        def __init__(self, host='127.0.0.1', port=8888):
            self.host = host
            self.port = port

    protocol = MagicMock()
    protocol.transport = MagicMock()
    protocol.transport.getPeer = MagicMock(return_value=Peer())

    nod = Node('public_key', 'private_key', screen)
    host = '127.0.0.1'
    port = 8888
    nod._contacts[(host, port)] = protocol

    msg = {
        'type': 'message',
        'message': 'hello'
    }
    nod.message_received(msg, protocol)
    assert 1 == nod._screen.addLine.call_count
    assert '[THEM] hello\n' == nod._screen.addLine.call_args[0][0]


def test_send_message():
    nod = Node('public_key', 'private_key', MagicMock())
    host = '127.0.0.1'
    port = 8888
    protocol = MagicMock()
    nod._contacts[(host, port)] = protocol
    msg = {
        'type': 'message',
        'message': 'hello'
    }
    nod.send_message(host, port, msg)
    assert 1 == protocol.sendMessage.call_count
    assert msg == protocol.sendMessage.call_args[0][0]
