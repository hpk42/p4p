import sys
import py
import time
import threading
tw = py.io.TerminalWriter()

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

getch = _GetchUnix()


class Buffer:
    def __init__(self):
        self.read_so_far = ""

    def raw_input(self):
        while 1:
            c = getch()
            self.read_so_far += c
            if c == "\x03":
                raise KeyboardInterrupt()
            sys.stdout.write(c)
            sys.stdout.flush()

    def reline(self, msg):
        tw.reline(msg + " " * len(self.read_so_far))
        tw.write("\n")
        tw.write(self.read_so_far)

buffer = Buffer()

def me():
    for i in range(10):
        buffer.reline("\rhello" + str(i))
        time.sleep(3)

t = threading.Thread(target=me)
t.setDaemon(True)
t.start()

buffer.raw_input()

