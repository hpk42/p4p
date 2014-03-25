#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The UI for a simple chat application.
"""
import sys
import socket
import requests
import json

from argparse import ArgumentParser
from twisted.internet import reactor, defer
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers

from node import Node
from protocol import MessageFactory
from friendsecure import crypto, contacts, console


# object with property access for global configuration
class Config(object):

    def update(self, data):
        vars(self).update(data)


config = Config()


def lookup_url(fingerprint):
    return '%s/%s' % (config.lookup_url.rstrip('/'), fingerprint)


def get_user_info(fingerprint):
    """
    fingerprint = the user's fingerprint

    Returns a deferred that fires with the resulting JSON to which you should
    add call/errbacks.

    Yes, this is a Twisted ball of deferreds and callbacks. :-(
    """
    d = defer.Deferred()
    def body_callback(body):
        d.callback(json.loads(body))

    def request_callback(response):
        body = readBody(response)
        body.addCallback(body_callback)

    agent = Agent(reactor)
    request = agent.request(
        'GET',
        lookup_url(fingerprint),
        Headers({}),
        None
    )
    request.addCallback(request_callback)
    return d


def post_user_info():
    """
    Must be called before reactor starts.

    HACKY!
    """
    hostname = socket.gethostname()
    if not hostname.endswith('.local'):
        hostname += '.local'
    address = socket.gethostbyname(hostname)
    presence = json.dumps({
        'hostname': hostname,       # TODO: remove, only for debugging
        'ip_address': address,
        'port': config.port
    })
    data = json.dumps(config.key.sign_message(presence))
    return requests.post(lookup_url(config.key.fingerprint), data=data)


def prompt():
    while True:
        message = console.get_input()
        reactor.callFromThread(dispatch, message)


def dispatch(message):
    console.display('[YOU] ' + message)
    if message.startswith('co '):
        connect_to_peer(message)
    else:
        send_message(message)


def connect_to_peer(raw):
    args = raw.strip().split(' ')
    if len(args) == 2:
        def fingerprint_callback(result):
            details = json.loads(result['result']['message'])
            host = details['ip_address']
            port = details['port']
            config.peer = host, port
            console.display('Connecting to %s %d' % (host, port))
            config.node.send_message(host, port, {'type': 'connect',})

        peer_fingerprint = config.contacts.get_fingerprint(args[1])
        d = get_user_info(peer_fingerprint)
        d.addCallback(fingerprint_callback)
    else:
        console.display('INCORRECT ARGS: co fingerprint')


def send_message(raw):
    try:
        if config.peer is not None:
            host, port = config.peer
            config.node.send_message(host, port,
                {'type': 'message', 'message': raw})
        else:
            console.display('PLEASE CONNECT TO A PEER: "co "')
    except:
        pass


def parse_arguments():
    parser = ArgumentParser(description='Friendsecure chat client.')
    parser.add_argument('--lookup-url', default='http://teta.local:8080',
        help='url of lookup service')
    parser.add_argument('-p', '--port', default=8888, type=int,
        help='port to listen on for incoming messages')
    return parser.parse_args()


def main():
    config.update(vars(parse_arguments()))
    config.key = crypto.get_my_key()
    config.contacts = contacts.Contacts("contacts.json")
    result = post_user_info()
    if result.status_code >= 400:
        sys.exit("Couldn't POST to friend server")
    config.node = node = Node('foo', 'bar', config)
    config.peer = None
    reactor.listenTCP(config.port, MessageFactory(node))
    reactor.callInThread(prompt)
    console.display('Fingerprint: %s' % config.key.fingerprint)
    reactor.run() # have fun!
