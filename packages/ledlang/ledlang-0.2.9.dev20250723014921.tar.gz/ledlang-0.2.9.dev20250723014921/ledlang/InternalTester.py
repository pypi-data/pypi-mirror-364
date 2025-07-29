import os
import pty
import serial
import threading


class PytestLEDDeviceSimulator:
    def __init__(self, size="5x5"):
        self.master_fd, self.slave_fd = pty.openpty()
        self.slave_name = os.ttyname(self.slave_fd)
        self.serial = serial.Serial(self.slave_name, 115200, timeout=0.1)

        try:
            width_str, height_str = size.lower().split('x')
            self.width = int(width_str)
            self.height = int(height_str)
        except Exception:
            self.width = 5
            self.height = 5

        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self._running = True

    def run(self):
        with os.fdopen(self.master_fd, 'rb+', buffering=0) as master:
            buffer = b''
            while self._running:
                byte = master.read(1)
                if not byte:
                    continue
                if byte == b'\n':
                    line = buffer.decode('utf-8').strip()
                    buffer = b''
                    self._handle_command(line)
                else:
                    buffer += byte

    def _handle_command(self, command: str):
        parts = command.strip().split()
        if not parts:
            return

        cmd = parts[0].upper()
        if cmd == "PLOT" and len(parts) == 3:
            try:
                x, y = int(parts[1]), int(parts[2])
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y][x] = 1
            except ValueError:
                pass
        elif cmd == "CLEAR":
            self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def kill(self):
        self._running = False
        if self.serial.is_open:
            self.serial.close()
        return self.grid
