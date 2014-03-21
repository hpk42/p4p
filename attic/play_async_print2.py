# based on http://stackoverflow.com/questions/2082387/reading-input-from-raw-input-without-having-the-prompt-overwritten-by-other-th

from rl import readline
from threading import Thread, Timer

from sys import stdout
from struct import unpack
from fcntl import ioctl
from termios import TIOCGWINSZ


prompt = '> '


def clear_readline():
    # Next line said to be reasonably portable for various Unixes
    _, cols = unpack('hh', ioctl(stdout, TIOCGWINSZ, '1234'))
    length = len(readline.get_line_buffer()) + len(prompt)
    lines = length / cols
    # ANSI escape sequences (All VT100 except ESC[0G)
    stdout.write('\x1b[2K')                 # Clear current line
    stdout.write('\x1b[1A\x1b[2K' * lines)  # Move cursor up and clear line
    stdout.write('\x1b[0G')                 # Move to start of line


def interrupt():
    clear_readline()
    print('Interrupting cow -- moo!')
    readline.redisplay(True)
    Timer(2, interrupt).start()


def cli():
    while True:
        raw_input(prompt)


if __name__ == '__main__':
    Thread(target=cli).start()
    Timer(2, interrupt).start()
