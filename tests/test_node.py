from friendsecure.node import Node
from mock import MagicMock
import json


def test_message_received():
    pass


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
