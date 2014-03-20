#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The UI for a simple chat application.
"""
import sys
import getpass
import socket
import requests
import json
import curses
import curses.wrapper

from argparse import ArgumentParser
from twisted.internet import reactor, defer
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from twisted.python import log

from node import Node
from protocol import MessageFactory
from friendsecure import crypto


config = dict()


def lookup_url(fingerprint):
    return '%s/%s' % (config['lookup_url'].rstrip('/'), fingerprint)


def get_user_info(fingerprint):
    """
    fingerprint = the user's fingerprint

    Returns a deferred that fires with the resulting JSON to which you should
    add call/errbacks.

    Yes, this is a Twisted ball of deferreds and callbacks. :-(
    """
    d = defer.Deferred()
    def body_callback(body):
        print body
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


def post_user_info(fingerprint, port):
    """
    Must be called before reactor starts.

    HACKY!
    """
    hostname = socket.gethostname()
    if not hostname.endswith('.local'):
        hostname += '.local'
    address = socket.gethostbyname(hostname)
    me = {
        'hostname': hostname,
        'ip_address': address,
        'port': port
    }
    data = {
        "key": fingerprint,
        "message":  me,
        "signature": 'blob'
    }
    return requests.post(lookup_url(fingerprint), data=json.dumps(data))


class CursesStdIO:
    """
    Fake fd to be registered as a reader with the twisted reactor.
    Curses classes needing input should extend this.
    """

    def fileno(self):
        """
        We want to select on FD 0
        """
        return 0

    def doRead(self):
        """
        Called when input is ready
        """
        pass

    def logPrefix(self):
        return 'CursesClient'


class Screen(CursesStdIO):
    def __init__(self, stdscr):
        self.timer = 0
        self.statusText = "TEST CURSES APP -"
        self.searchText = ''
        self.stdscr = stdscr

        # set screen attributes
        self.stdscr.nodelay(1) # this is used to make input calls non-blocking
        curses.cbreak()
        self.stdscr.keypad(1)
        curses.curs_set(0)     # no annoying mouse cursor

        self.rows, self.cols = self.stdscr.getmaxyx()
        self.lines = []

        curses.start_color()

        # create color pair's 1 and 2
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)

        self.paintStatus(self.statusText)

        self.peer_host = ''
        self.peer_port = 0

    def connectionLost(self, reason):
        self.close()

    def addLine(self, text):
        """ add a line to the internal list of lines"""

        self.lines.append(text)
        self.redisplayLines()

    def redisplayLines(self):
        """ method for redisplaying lines
            based on internal list of lines """

        self.stdscr.clear()
        self.paintStatus(self.statusText)
        i = 0
        index = len(self.lines) - 1
        while i < (self.rows - 3) and index >= 0:
            self.stdscr.addstr(self.rows - 3 - i, 0, self.lines[index],
                               curses.color_pair(2))
            i = i + 1
            index = index - 1
        self.stdscr.refresh()

    def paintStatus(self, text):
        if len(text) > self.cols: raise TextTooLongError
        self.stdscr.addstr(self.rows-2,0,text + ' ' * (self.cols-len(text)),
                           curses.color_pair(1))
        # move cursor to input line
        self.stdscr.move(self.rows-1, self.cols-1)

    def doRead(self):
        """ Input is ready! """
        curses.noecho()
        self.timer = self.timer + 1
        c = self.stdscr.getch() # read a character

        if c == curses.KEY_BACKSPACE:
            self.searchText = self.searchText[:-1]

        elif c == curses.KEY_ENTER or c == 10:
            self.addLine('[YOU] ' + self.searchText)
            if self.searchText.startswith('co'):
                args = self.searchText.split(' ')
                if len(args) == 2:
                    def fingerprint_callback(result):
                        details = result['result']['message']
                        self.peer_host = details['ip_address']
                        self.peer_port = details['port']
                        self.addLine('Connecting to %s %d' % (self.peer_host,
                                     self.peer_port))
                        self._node.send_message(self.peer_host,
                                                self.peer_port,
                                                {'type': 'connect',})

                    peer_fingerprint = args[1]
                    d = get_user_info(peer_fingerprint)
                    d.addCallback(fingerprint_callback)
                else:
                    self.addLine('INCORRECT ARGS: co fingerprint')
            else:
                try:
                    if self.peer_host and self.peer_port:
                        self._node.send_message(self.peer_host,
                                                self.peer_port,
                                                {'type': 'message',
                                                 'message': self.searchText})
                    else:
                        self.addLine('PLEASE CONNECT TO A PEER: "co ip port"')
                except:
                    pass
            self.stdscr.refresh()
            self.searchText = ''
        else:
            if len(self.searchText) == self.cols-2:
                return
            self.searchText = self.searchText + chr(c)

        self.stdscr.addstr(self.rows-1, 0,
                           self.searchText + (' ' * (
                           self.cols-len(self.searchText)-2)))
        self.stdscr.move(self.rows-1, len(self.searchText))
        self.paintStatus(self.statusText + ' %d' % len(self.searchText))
        self.stdscr.refresh()

    def close(self):
        """ clean up """

        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()


def parse_arguments():
    parser = ArgumentParser(description='Friendsecure chat client.')
    parser.add_argument('--lookup-url', default='http://teta.local:8080',
        help='url of lookup service')
    parser.add_argument('-p', '--port', default=8888, type=int,
        help='port to listen on for incoming messages')
    return parser.parse_args()


def main():
    args = parse_arguments()
    config.update(vars(args))
    fingerprint = crypto.fingerprint(crypto.get_my_key())
    result = post_user_info(fingerprint, args.port)
    if result.status_code >= 400:
        sys.exit("Couldn't POST to friend server")
    stdscr = curses.initscr() # initialize curses
    screen = Screen(stdscr)   # create Screen object
    stdscr.refresh()
    n = Node('foo', 'bar', screen)
    screen._node = n
    reactor.listenTCP(args.port, MessageFactory(n))
    reactor.addReader(screen) # add screen object as a reader to the reactor
    screen.addLine('Fingerprint: %s' % fingerprint)
    reactor.run() # have fun!
    screen.close()
