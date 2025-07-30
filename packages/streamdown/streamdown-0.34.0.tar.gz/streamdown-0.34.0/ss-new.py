import os
import pty
import sys
import tty
import termios
import select
import re

def main():
    orig_attrs = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin)
        pid, fd = pty.fork()

        if pid == 0:
            # Child process: run any command
            os.execvp("llm", ["llm", "chat"])
        else:
            buffer = b""

            while True:
                r, _, _ = select.select([fd, sys.stdin], [], [])

                if sys.stdin in r:
                    data = os.read(sys.stdin.fileno(), 1024)
                    if not data:
                        break
                    os.write(fd, data)

                if fd in r:
                    data = os.read(fd, 1024)
                    if not data:
                        break

                    buffer += data
                    # Replace "fizz" only in printable content
                    output = re.sub(rb'fizz', b'fizzbuzz', buffer)
                    os.write(sys.stdout.fileno(), output)
                    buffer = b""
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_attrs)

if __name__ == "__main__":
    main()

