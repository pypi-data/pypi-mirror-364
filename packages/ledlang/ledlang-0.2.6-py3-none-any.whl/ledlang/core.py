import time
import re
import os
import logging

# Full 5x5 font including uppercase letters, digits, and common punctuation
FONT_5x5 = {
    # Letters A-Z
    'A': ["01110",
          "10001",
          "11111",
          "10001",
          "10001"],

    'B': ["11110",
          "10001",
          "11110",
          "10001",
          "11110"],

    'C': ["01111",
          "10000",
          "10000",
          "10000",
          "01111"],

    'D': ["11110",
          "10001",
          "10001",
          "10001",
          "11110"],

    'E': ["11111",
          "10000",
          "11110",
          "10000",
          "11111"],

    'F': ["11111",
          "10000",
          "11110",
          "10000",
          "10000"],

    'G': ["01111",
          "10000",
          "10011",
          "10001",
          "01111"],

    'H': ["10001",
          "10001",
          "11111",
          "10001",
          "10001"],

    'I': ["11111",
          "00100",
          "00100",
          "00100",
          "11111"],

    'J': ["00111",
          "00010",
          "00010",
          "10010",
          "01100"],

    'K': ["10001",
          "10010",
          "11100",
          "10010",
          "10001"],

    'L': ["10000",
          "10000",
          "10000",
          "10000",
          "11111"],

    'M': ["10001",
          "11011",
          "10101",
          "10001",
          "10001"],

    'N': ["10001",
          "11001",
          "10101",
          "10011",
          "10001"],

    'O': ["01110",
          "10001",
          "10001",
          "10001",
          "01110"],

    'P': ["11110",
          "10001",
          "11110",
          "10000",
          "10000"],

    'Q': ["01110",
          "10001",
          "10001",
          "10011",
          "01111"],

    'R': ["11110",
          "10001",
          "11110",
          "10010",
          "10001"],

    'S': ["01111",
          "10000",
          "01110",
          "00001",
          "11110"],

    'T': ["11111",
          "00100",
          "00100",
          "00100",
          "00100"],

    'U': ["10001",
          "10001",
          "10001",
          "10001",
          "01110"],

    'V': ["10001",
          "10001",
          "10001",
          "01010",
          "00100"],

    'W': ["10001",
          "10001",
          "10101",
          "11011",
          "10001"],

    'X': ["10001",
          "01010",
          "00100",
          "01010",
          "10001"],

    'Y': ["10001",
          "01010",
          "00100",
          "00100",
          "00100"],

    'Z': ["11111",
          "00010",
          "00100",
          "01000",
          "11111"],

    # Digits 0-9
    '0': ["01110",
          "10011",
          "10101",
          "11001",
          "01110"],

    '1': ["00100",
          "01100",
          "00100",
          "00100",
          "01110"],

    '2': ["01110",
          "10001",
          "00010",
          "00100",
          "11111"],

    '3': ["11111",
          "00010",
          "00100",
          "10001",
          "01110"],

    '4': ["00010",
          "00110",
          "01010",
          "11111",
          "00010"],

    '5': ["11111",
          "10000",
          "11110",
          "00001",
          "11110"],

    '6': ["01110",
          "10000",
          "11110",
          "10001",
          "01110"],

    '7': ["11111",
          "00001",
          "00010",
          "00100",
          "00100"],

    '8': ["01110",
          "10001",
          "01110",
          "10001",
          "01110"],

    '9': ["01110",
          "10001",
          "01111",
          "00001",
          "01110"],

    # Common punctuation
    '.': ["00000",
          "00000",
          "00000",
          "00110",
          "00110"],

    ',': ["00000",
          "00000",
          "00000",
          "00110",
          "00100"],

    '!': ["00100",
          "00100",
          "00100",
          "00000",
          "00100"],

    '?': ["01110",
          "10001",
          "00010",
          "00000",
          "00100"],

    '-': ["00000",
          "00000",
          "11111",
          "00000",
          "00000"],

    '+': ["00000",
          "00100",
          "01110",
          "00100",
          "00000"],

    ':': ["00000",
          "00110",
          "00000",
          "00110",
          "00000"],

    ';': ["00000",
          "00110",
          "00000",
          "00100",
          "01000"],

    '\'':["00100",
          "00100",
          "00000",
          "00000",
          "00000"],

    '"': ["01010",
          "01010",
          "00000",
          "00000",
          "00000"],

    '(': ["00010",
          "00100",
          "00100",
          "00100",
          "00010"],

    ')': ["01000",
          "00100",
          "00100",
          "00100",
          "01000"],

    '[': ["01110",
          "01000",
          "01000",
          "01000",
          "01110"],

    ']': ["01110",
          "00010",
          "00010",
          "00010",
          "01110"],

    '{': ["00010",
          "00100",
          "01000",
          "00100",
          "00010"],

    '}': ["01000",
          "00100",
          "00010",
          "00100",
          "01000"],

    '<': ["00010",
          "00100",
          "01000",
          "00100",
          "00010"],

    '>': ["01000",
          "00100",
          "00010",
          "00100",
          "01000"],

    '/': ["00001",
          "00010",
          "00100",
          "01000",
          "10000"],

    '@': ["01110",
          "10001",
          "10111",
          "10000",
          "01110"],

    '#': ["01010",
          "11111",
          "01010",
          "11111",
          "01010"],

    '$': ["00100",
          "01111",
          "10100",
          "01111",
          "00100"],

    '%': ["11001",
          "11010",
          "00100",
          "01011",
          "10011"],

    '^': ["00100",
          "01010",
          "10001",
          "00000",
          "00000"],

    '&': ["01100",
          "10010",
          "01100",
          "10010",
          "01101"],

    '*': ["00000",
          "10101",
          "01110",
          "10101",
          "00000"],

    '_': ["00000",
          "00000",
          "00000",
          "00000",
          "11111"],

    '=': ["00000",
          "11111",
          "00000",
          "11111",
          "00000"],

    '~': ["00000",
          "01001",
          "10110",
          "00000",
          "00000"],
}
def bresenham_line(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
        points.append((x, y))
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
        points.append((x, y))
    return points

class LEDLang:
    def __init__(self, serial_obj):
        self.ser = serial_obj
        self.width = 5
        self.height = 5
        self.folder = None
        self.compiled = {}
        self.funcs = {}
        self.real_width = self.width 
        self.real_height = self.height

    def send(self, command):
        baud = self.ser.baudrate
        length = len(command.strip()) + 2
        tx_time = (length * 10) / baud
        proc_time = 0.015 if command.strip().upper().startswith("CLEAR") else 0.003 if command.strip().upper().startswith("PLOT") else 0.005
        total = tx_time + proc_time
        if total > 0.02:
            logging.warning(f"Wait time {total:.4f}s for command '{command}' exceeds 0.02 seconds")

        self.ser.write((command.strip() + "\r\n").encode())
        self.ser.flush()
        time.sleep(total)

    def normalize_rotation(self, angle):
        angle = angle % 360
        if angle < 0:
            angle += 360
        return angle
    
    def rotate_point(self, x, y, angle):
        w, h = self.width, self.height
        angle = self.normalize_rotation(angle)
        if angle == 0:
            return x, y
        elif angle == 90:
            return h - 1 - y, x
        elif angle == 180:
            return w - 1 - x, h - 1 - y
        elif angle == 270:
            return y, w - 1 - x

    def set_folder(self, folder_path):
        if not os.path.isdir(folder_path):
            raise ValueError(f"Folder does not exist: {folder_path}")
        self.folder = folder_path
        self.compiled.clear()
        for file in os.listdir(folder_path):
            if file.endswith(".led"):
                path = os.path.join(folder_path, file)
                with open(path, "r") as f:
                    code = f.read()
                key = file[:-4]
                self.compiled[key] = self.compile(code)

    def playfile(self, filename):
        if filename.endswith(".led"):
            filename = filename[:-4]
        if filename not in self.compiled:
            raise ValueError(f"File not compiled: {filename}")
        self.play(self.compiled[filename])

    def compile(self, code, rotation=0, width=None, height=None):
        cmds = []
        lines = code.strip().splitlines()
        i = 0
        rotation = 0  # rotation angle in degrees
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        while i < len(lines):
            line = lines[i].strip()

            if line.startswith("INIT"):
                size = re.findall(r"(\d+)x(\d+)", line)
                if size:
                    width, height = map(int, size[0])
                    self.real_width, self.real_height = map(int, size[0])
                    cmds.append({'cmd':'CLEAR'})

            elif line.startswith("REALSIZE"):
                size = re.findall(r"(\d+)x(\d+)", line)
                if size:
                    self.real_width, self.real_height = map(int, size[0])
                    cmds.append({'cmd':'CLEAR'})


            elif line.startswith("CLEAR"):
                cmds.append({'cmd':'CLEAR'})

            elif line.startswith("ROTATE"):
                parts = line.split()
                if len(parts) == 1:
                    angle = 90
                else:
                    try:
                        angle = int(parts[1])
                    except:
                        angle = 90
                rotation = self.normalize_rotation(rotation + angle)
                cmds.append({'cmd':'CLEAR'})

            elif line.startswith("PLOT"):
                parts = line.split()
                if len(parts) == 3:
                    try:
                        x, y = int(parts[1]), int(parts[2])
                        rx, ry = self.rotate_point(x, y, rotation)
                        cmds.append({'cmd':'PLOT','x': rx,'y': ry})
                    except:
                        pass

            elif line.startswith("LINE"):
                parts = line.split()
                if len(parts) == 5:
                    try:
                        x1, y1, x2, y2 = map(int, parts[1:])
                        points = bresenham_line(x1, y1, x2, y2)
                        for (x, y) in points:
                            rx, ry = self.rotate_point(x, y, rotation)
                            if 0 <= rx < width and 0 <= ry < height:
                                cmds.append({'cmd':'PLOT','x': rx,'y': ry})
                    except:
                        pass

            elif line.startswith("WAIT"):
                secs = float(re.findall(r"WAIT\s+\[?([0-9.]+)\]?", line)[0])
                cmds.append({'cmd':'WAIT', 'sec': secs})

            elif line.startswith("PROGRESS"):
                parts = line.split()
                if 5 <= len(parts) <= 6:
                    try:
                        x1, y1, x2, y2 = map(int, parts[1:5])
                        delay = float(parts[5]) if len(parts) == 6 else 0.1
                        points = bresenham_line(x1, y1, x2, y2)
                        for (x, y) in points:
                            rx, ry = self.rotate_point(x, y, rotation)
                            if 0 <= rx < width and 0 <= ry < height:
                                cmds.append({'cmd': 'PLOT', 'x': rx, 'y': ry})
                                cmds.append({'cmd': 'WAIT', 'sec': delay})
                    except:
                        pass

            elif line.startswith("FILL"):
                parts = line.split()
                if len(parts) == 5:
                    try:
                        x1, y1, x2, y2 = map(int, parts[1:])
                        xmin, xmax = sorted((x1, x2))
                        ymin, ymax = sorted((y1, y2))
                        for y in range(ymin, ymax + 1):
                            for x in range(xmin, xmax + 1):
                                rx, ry = self.rotate_point(x, y, rotation)
                                if 0 <= rx < width and 0 <= ry < height:
                                    cmds.append({'cmd':'PLOT', 'x': rx, 'y': ry})
                    except:
                        pass
                    
            elif line.startswith("OUTLINE"):
                parts = line.split()
                if len(parts) == 5:
                    try:
                        x1, y1, x2, y2 = map(int, parts[1:])
                        xmin, xmax = sorted((x1, x2))
                        ymin, ymax = sorted((y1, y2))
                        # Top and bottom edges
                        for x in range(xmin, xmax + 1):
                            for y in (ymin, ymax):
                                rx, ry = self.rotate_point(x, y, rotation)
                                if 0 <= rx < width and 0 <= ry < height:
                                    cmds.append({'cmd':'PLOT', 'x': rx, 'y': ry})
                        # Left and right edges (excluding corners already drawn)
                        for y in range(ymin + 1, ymax):
                            for x in (xmin, xmax):
                                rx, ry = self.rotate_point(x, y, rotation)
                                if 0 <= rx < width and 0 <= ry < height:
                                    cmds.append({'cmd':'PLOT', 'x': rx, 'y': ry})
                    except:
                        pass

            elif line.startswith("#"):
                pass

            elif line.startswith("DISPLAY"):
                i += 1
                image = []
                while i < len(lines):
                    display_line = lines[i].strip()
                    if display_line == "]":
                        break
                    image.append(display_line.replace(" ", ""))
                    i += 1

                img_width = max(len(row) for row in image) if image else 0
                img_height = len(image)

                if img_width > width and img_height <= height:
                    max_scroll = img_width - width  # how many scroll steps needed

                    for scrollX in range(max_scroll + 1):  # +1 to show last frame fully scrolled
                        cmds.append({'cmd': 'CLEAR'})
                        for y, row in enumerate(image):
                            for x, pixel in enumerate(row):
                                if pixel == "1":
                                    plot_x = x - scrollX
                                    if 0 <= plot_x < width and y < height:
                                        rx, ry = self.rotate_point(plot_x, y, rotation)
                                        cmds.append({'cmd': 'PLOT', 'x': rx, 'y': ry})
                        cmds.append({'cmd': 'WAIT', 'sec': 0.2})

                else:
                    # Image fits width or height, no scroll needed
                    cmds.append({'cmd': 'CLEAR'})
                    for y, row in enumerate(image):
                        for x, pixel in enumerate(row):
                            if pixel == "1" and x < width and y < height:
                                rx, ry = self.rotate_point(x, y, rotation)
                                cmds.append({'cmd': 'PLOT', 'x': rx, 'y': ry})

            elif line.startswith("STARTFUNC"):
                i += 1
                newcode = ""
                split = line.split()
                while i < len(lines) and not lines[i].strip().startswith("ENDFUNC"):
                    newcode += lines[i].strip() + "\n"
                    i += 1
                self.funcs[split[1]] = self.compile(newcode)

            elif line.startswith("CALLFUNC"):
                parts = line.split()
                if len(parts) == 2:
                    cmds.extend(self.funcs[parts[1]])

            elif line.startswith("TEXT"):
                m = re.findall(r'TEXT\s*\[([^\]]+)\]', line)
                if m:
                    text = m[0]
                else:
                    parts = line.split(maxsplit=1)
                    text = parts[1] if len(parts) > 1 else ""
                text = text.upper()

                if not text:
                    i += 1
                    continue

                if len(text) == 1:
                    cmds.append({'cmd':'CLEAR'})
                    letter_bitmap = self.get_letter_bitmap(text)
                    for y, row in enumerate(letter_bitmap):
                        for x, pixel in enumerate(row):
                            if pixel == '1' and x < width and y < height:
                                rx, ry = self.rotate_point(x, y, rotation)
                                cmds.append({'cmd':'PLOT', 'x': rx, 'y': ry})
                    cmds.append({'cmd':'WAIT', 'sec': 1})

                else:
                    full_bitmap = self.build_text_bitmap(text)
                    for offset in range(len(full_bitmap[0]) - width + 1):
                        cmds.append({'cmd':'CLEAR'})
                        for y in range(height):
                            for x in range(width):
                                if full_bitmap[y][x + offset] == '1':
                                    rx, ry = self.rotate_point(x, y, rotation)
                                    cmds.append({'cmd':'PLOT', 'x': rx, 'y': ry})
                        cmds.append({'cmd':'WAIT', 'sec': 0.3})

            i += 1

        return cmds
    def play(self, obj):
        cmds = obj
        scale_x = max(1, self.real_width // self.width)
        scale_y = max(1, self.real_height // self.height)
        for c in cmds:
            logging.debug("Sending command: %s", c)
            if isinstance(c, dict) and 'cmd' in c:
                if c['cmd'] == 'CLEAR':
                    self.send('CLEAR')
                elif c['cmd'] == 'PLOT':
                    base_x, base_y = c['x'], c['y']
                    for dx in range(scale_x):
                        for dy in range(scale_y):
                            sx = base_x * scale_x + dx
                            sy = base_y * scale_y + dy
                            self.send(f"PLOT {sx} {sy}")
                elif c['cmd'] == 'WAIT':
                    time.sleep(c['sec'])
            else:
                logging.warning("Unknown command format: %s", c)

    def get_letter_bitmap(self, char):
        base = FONT_5x5.get(char, FONT_5x5['.'])
        if self.width == 5 and self.height == 5:
            return base

        resized = []
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                src_x = int(x * 5 / self.width)
                src_y = int(y * 5 / self.height)
                row += base[src_y][src_x]
            resized.append(row)
        return resized

    def build_text_bitmap(self, text):
        letters = [self.get_letter_bitmap(c) for c in text]
        rows = ['' for _ in range(self.height)]
        for letter in letters:
            for y in range(self.height):
                rows[y] += letter[y] + '0'  # space between letters
        return rows
