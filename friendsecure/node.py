# -*- coding: utf-8 -*-
"""
Contains code that defines the behaviour of the local node.
"""

from twisted.internet import reactor, defer
from twisted.internet.endpoints import clientFromString
from protocol import MessageFactory
from friendsecure.console import display


class Node(object):
    """
    Represents the local node in the network.
    """

    def __init__(self, public_key, private_key, config):
        """
        Initialises the object representing the node with the given id.
        """
        self._public_key = public_key
        self._private_key = private_key
        self._contacts = {}
        self.config = config

    def message_received(self, message, protocol):
        """
        Handles incoming messages.
        """
        peer = protocol.transport.getPeer()
        self.config.peer = peer_key = (peer.host, peer.port)
        if peer_key not in self._contacts:
            self._contacts[peer_key] = protocol
        if 'type' not in message:
            protocol.error('Must specify message type.')
            return
        message_type = message['type']
        if message_type == 'connect':
            display('Connection from %s %d' % (peer.host, peer.port))
        else:
            display('[THEM] ' + message['message'])

    def send_message(self, host, port, message):
        """
        Sends a message to the specified contact, adds it to the _pending
        dictionary and ensures it times-out after the correct period. If an
        error occurs the deferred's errback is called.
        """
        peer_key = (host, port)
        if peer_key in self._contacts:
            protocol = self._contacts[peer_key]
            protocol.sendMessage(message)
            return
        d = defer.Deferred()
        # open network call.
        client_string = 'tcp:%s:%d' % (host, port)
        client = clientFromString(reactor, client_string)
        connection = client.connect(MessageFactory(self))
        # Ensure the connection attempt will time out after 5 seconds.
        connection_timeout = reactor.callLater(5, connection.cancel)

        def on_connect(protocol):
            # Cancel pending connection_timeout if it's still active.
            if connection_timeout.active():
                connection_timeout.cancel()
            self._contacts[peer_key] = protocol
            # Send the message
            protocol.sendMessage(message)

        def on_error(error):
            d.errback(error)

        connection.addCallback(on_connect)
        connection.addErrback(on_error)
