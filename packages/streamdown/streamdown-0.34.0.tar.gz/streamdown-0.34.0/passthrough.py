import os
import pty
import sys
import select
import tty
import termios
import subprocess

def passthrough(processor, command):
    if not command:
        print("Usage: passthrough <processor> <command> [args...]", file=sys.stderr)
        sys.exit(1)

    # Save original terminal settings
    original_settings = termios.tcgetattr(sys.stdin.fileno())

    try:
        pid, fd = pty.fork()
        if pid == 0:  # Child process
            os.execvp(command[0], command)  # Replace with target program
        else:  # Parent process
            tty.setraw(sys.stdin.fileno())  # Set raw mode for proper input handling
            
            # Start the processor subprocess
            processor_proc = subprocess.Popen(
                processor, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, text=False
            )

            while True:
                rlist, _, _ = select.select([fd, sys.stdin], [], [])
                if fd in rlist:
                    try:
                        data = os.read(fd, 10)
                        if not data:
                            break
                        processor_proc.stdin.write(data)
                        processor_proc.stdin.flush()
                    except (OSError, BrokenPipeError):
                        break
                if sys.stdin in rlist:
                    try:
                        data = os.read(sys.stdin.fileno(), 10)
                        if not data:
                            break
                        os.write(fd, data)  # Send input to child process
                    except OSError:
                        break
    finally:
        # Restore original terminal settings
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, original_settings)
        processor_proc.stdin.close()
        processor_proc.wait()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: passthrough <processor> <command> [args...]", file=sys.stderr)
        sys.exit(1)
    
    passthrough([sys.argv[1]], sys.argv[2:])

