import os
from .core import LEDLang
import serial
import pty
from typing import TypedDict, List, Union
import threading

class Display(TypedDict):
    serial: serial.Serial
    rotation: Union[int, float]

class Displays(TypedDict):
    size: str
    displays: List[Display]

class SingleDisplayToMulti:
    def __init__(self, master_fd, displays: Displays):
        self.master_fd = master_fd
        self.displays = displays
        size_str = self.displays["size"].lower()
        self.width, self.height = map(int, size_str.split('x'))

    def run(self):
        with os.fdopen(self.master_fd, 'rb+', buffering=0) as master:
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
        parts = command.strip().split()
        cmd = parts[0].upper()

        if cmd == "CLEAR":
            for disp in self.displays["displays"]:
                disp['serial'].write(b"CLEAR\n")
            return

        if cmd == "PLOT":
            if len(parts) != 3:
                return  # Invalid PLOT command format

            try:
                x = int(parts[1])
                y = int(parts[2])
            except ValueError:
                return  # Invalid coordinates

            # Check vertical bounds (y must fit display height)
            if y < 0 or y >= self.height:
                return  # y out of range

            # Determine which display horizontally
            display_index = x // self.width
            local_x = x % self.width

            if display_index >= len(self.displays["displays"]):
                return  # x out of all displays range

            disp = self.displays["displays"][display_index]
            rotation = disp.get('rotation', 0) % 360  # Normalize rotation

            # Apply rotation
            rx, ry = self.apply_rotation(local_x, y, rotation)

            # Compose and send command
            send_str = f"PLOT {rx} {ry}\n"
            disp['serial'].write(send_str.encode('ascii'))

    def apply_rotation(self, x, y, rotation):
        """
        Rotate (x, y) by rotation degrees clockwise on display of size width x height
        """
        w, h = self.width, self.height

        if rotation == 0:
            return x, y
        elif rotation == 90:
            # (x, y) -> (h - 1 - y, x)
            return h - 1 - y, x
        elif rotation == 180:
            # (x, y) -> (w - 1 - x, h - 1 - y)
            return w - 1 - x, h - 1 - y
        elif rotation == 270:
            # (x, y) -> (y, w - 1 - x)
            return y, w - 1 - x
        else:
            # If rotation is not one of the standard ones, approximate with modulo 360:
            # For non-90° multiples, just fallback to no rotation or raise error
            # You can expand this to support other rotations if needed
            return x, y

# Modify LEDLang class
class MultiLEDLang(LEDLang):
    def __init__(self, displays: Displays, wait=True):
        master_fd, slave_fd = pty.openpty()
        self.slave_name = os.ttyname(slave_fd)
        self.multi = SingleDisplayToMulti(master_fd, displays)
        super().__init__(serial.Serial(self.slave_name, 115200), wait)
        threading.Thread(target=self.multi.run, daemon=True).start()