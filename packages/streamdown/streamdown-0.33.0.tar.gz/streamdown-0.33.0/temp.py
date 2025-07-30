import sys
import os
import pty
import select
import termios
import tty

def main():
    # Save original terminal settings
    old_settings = termios.tcgetattr(sys.stdin.fileno())

    # Spawn a child process (e.g., 'cat' to echo input)
    # In a real scenario, this might be the process being debugged or interacted with.
    # For simplicity, we'll just use 'cat' which echoes stdin to stdout.
    # We don't actually need the child pid for this example.
    master_fd, slave_fd = pty.openpty()

    # Put the controlling terminal into raw mode
    tty.setraw(sys.stdin.fileno())

    try:
        while True:
            # Wait for input from stdin (piped, e.g., gdb) or the PTY master (keyboard)
            # We add a timeout just in case, but it's not strictly necessary here.
            ready, _, _ = select.select([sys.stdin.fileno(), master_fd], [], [], 0.1)

            # 1. Handle Piped Input (e.g., from gdb)
            if sys.stdin.fileno() in ready:
                piped_data = os.read(sys.stdin.fileno(), 1024)
                if not piped_data:
                    print("\r\nPiped input (stdin) closed.\r\n")
                    break # Exit if stdin closes
                # Process piped data (here, just print it)
                # Add carriage returns for raw mode visibility
                print(f"\r\n--- Received from stdin pipe: {piped_data.decode(errors='replace')} ---\r\n")


            # 2. Handle Keyboard Input via PTY
            if master_fd in ready:
                try:
                    pty_data = os.read(master_fd, 1024)
                    if not pty_data:
                        print("\r\nPTY master closed.\r\n")
                        break # Exit if PTY master closes (e.g., child exited)

                    # Echo keyboard input back to the terminal (handled by PTY usually,
                    # but explicit write ensures it appears)
                    os.write(sys.stdout.fileno(), pty_data)
                    sys.stdout.flush()

                    # Process keyboard data (here, just print it)
                    # Add carriage returns for raw mode visibility
                    print(f"\r\n--- Received from keyboard (PTY): {pty_data.decode(errors='replace')} ---\r\n")

                    # Example: Exit on Ctrl+D (EOF)
                    if b'\x04' in pty_data:
                         print("\r\nCtrl+D detected. Exiting.\r\n")
                         break

                except OSError:
                    # This can happen if the child process exits unexpectedly
                    print("\r\nOSError reading from PTY master.\r\n")
                    break

    finally:
        # Restore original terminal settings
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
        os.close(master_fd)
        # slave_fd is implicitly closed when the child process exits or master is closed

if __name__ == "__main__":
    print("Starting temp.py. Reading from stdin pipe and keyboard via PTY.")
    print("Type characters or pipe data. Press Ctrl+D in terminal to exit.")
    main()
    print("temp.py finished.")