# -*- coding: utf-8 -*-
"""
Contains a definition of the low-level networking protocol used by Meshage.

"""

from twisted.internet import protocol
from twisted.protocols.basic import NetstringReceiver
from uuid import uuid4
import json


class MeshageProtocol(NetstringReceiver):
    """
    The low level networking protocol.

    JSON encoded payloads are transported as netstrings
    (http://cr.yp.to/proto/netstrings.txt).

    The payload is simply a dictionary of attributes. It is assumed the the
    higher levels of the application understand the dicts.

    To the external world messages come in, messages go out (and implementation
    details are hidden).
    """
    def error(self, description=None):
        """
        Returns an error message with an optional description.
        """
        message = {'type': 'error'}
        if description:
            message['description'] = description
        self.sendMessage(message)

    def stringReceived(self, raw):
        """
        Handles incoming requests by unpacking them before passing them to
        the Node instance for further processing. If the message cannot be
        unpacked or is invalid an appropriate error message is returned to
        the originating caller.
        """
        try:
            message = json.loads(raw)
            print '%r' % message
            self.factory.node.message_received(message, self)
        except Exception, ex:
            # Catch all for anything unexpected
            description = '%r' % ex
            self.error(description)

    def sendMessage(self, msg):
        """
        Sends the referenced message to the connected peer on the network.
        """
        # TODO: Add other meta things here. Message signature perhaps..?
        self.sendString(json.dumps(msg))


class MeshageFactory(protocol.Factory):
    """
    Meshage Factory class that uses the MeshageProtocol.
    """

    protocol = MeshageProtocol

    def __init__(self, node):
        """
        Instantiates the factory with a node object representing the local
        node within the network.
        """
        self.node = node
