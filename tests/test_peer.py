from friendsecure.node import Node
from friendsecure.peer import send_message
from mock import MagicMock
import json


def test_send_message():
    nod = Node('public_key', 'private_key', MagicMock())
    host = '127.0.0.1'
    port = 8888
    nod.send_message = MagicMock()

    class Screen(object):
        def __init__(self):
            self.addLine = MagicMock()
            self.peer_host = host
            self.peer_port = port
            self._node = nod

    screen = Screen()

    send_message(screen, 'hello')
    assert 1 == screen._node.send_message.call_count
    assert host == screen._node.send_message.call_args[0][0]
    assert port == screen._node.send_message.call_args[0][1]
    expected = {'type': 'message', 'message': 'hello'}
    assert expected == screen._node.send_message.call_args[0][2]
