from .core import LEDLang
import serial
import pty
import os
import threading
import argparse
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Set the file to save to
log_file = 'ledlang-test.log'
handler = logging.FileHandler(log_file)
handler.setLevel(logging.DEBUG)

# ANSI color codes for terminal output
WHITE = "\033[47m  \033[0m"
RED = "\033[41m  \033[0m"

class LEDDeviceSimulator:
    def __init__(self, master_fd, size="5x5"):
        self.master_fd = master_fd
        # Parse size string "WxH" into integers
        try:
            width_str, height_str = size.lower().split('x')
            self.width = int(width_str)
            self.height = int(height_str)
        except Exception:
            # Fallback to 5x5 if parse fails
            self.width = 5
            self.height = 5
        self.grid = [['WHITE' for _ in range(self.width)] for _ in range(self.height)]

    def print_grid(self):
        os.system('clear')  # clear terminal screen on update (Linux/macOS)
        print(f"{self.width}x{self.height} LED Grid (WHITE = empty, RED = lit):")
        for row in self.grid:
            line = ''
            for color in row:
                if color == 'WHITE':
                    line += WHITE
                elif color == 'RED':
                    line += RED
            print(line)
        print("\nWaiting for commands...")

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = color

    def clear_grid(self):
        self.grid = [['WHITE' for _ in range(self.width)] for _ in range(self.height)]

    def run(self):
        with os.fdopen(self.master_fd, 'rb+', buffering=0) as master:
            self.clear_grid()
            self.print_grid()
            buffer = b''
            while True:
                byte = master.read(1)
                if not byte:
                    continue
                if byte == b'\n':
                    line = buffer.decode('utf-8').strip()
                    buffer = b''
                    self.handle_command(line)
                else:
                    buffer += byte

    def handle_command(self, command):
        parts = command.split()
        if not parts:
            return
        cmd = parts[0].upper()
        if cmd == 'PLOT' and len(parts) == 3:
            try:
                x = int(parts[1])
                y = int(parts[2])
                self.set_pixel(x, y, 'RED')
                self.print_grid()
            except ValueError:
                pass
        elif cmd == 'CLEAR':
            self.clear_grid()
            self.print_grid()
        else:
            raise ValueError(f"Unknown command: {command}\nOn the real device, this would reset the device and return an error.")

def main():
    parser = argparse.ArgumentParser(description="LEDLang Tester.")
    parser.add_argument("--folder", help="Folder that contains the LEDLang files. Defaults to the libs tests folder.", default=os.path.abspath(os.path.dirname(__file__) + "/tests"))
    parser.add_argument("animation", help="The file to play, without the .led extension.")
    parser.add_argument("--size", help="The size of the grid to use (e.g., 5x5).", default="5x5")
    args = parser.parse_args()

    # Setup virtual serial port pair
    master_fd, slave_fd = pty.openpty()
    slave_name = os.ttyname(slave_fd)

    # Start the device simulator in a thread
    simulator = LEDDeviceSimulator(master_fd, args.size)
    threading.Thread(target=simulator.run, daemon=True).start()

    with serial.Serial(slave_name, 115200, timeout=1) as ser:
        logging.info(f"Listening on {slave_name} at 115200 baud...")

        LED = LEDLang(ser)
        LED.set_folder(args.folder)
        LED.playfile(args.animation)

if __name__ == "__main__":
    main()
