from .core import LEDLang
import serial
from pathlib import Path
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="LEDLang CLI Sender.")
    parser.add_argument("--folder", help="Folder that contains the LEDLang files. Defaults to the libs tests folder.", default=os.path.abspath(os.path.dirname(__file__) + "/tests"))
    parser.add_argument("animation", help="The file to play, without the .led extension.")
    parser.add_argument("serial", type=Path, help="The serial port to connect to (e.g., /dev/ttyUSB0).")
    parser.add_argument("--baudrate", type=int, help="The baud rate to use (e.g., 115200).", default=115200)
    args = parser.parse_args()
    args.serial = str(args.serial) 

    with serial.Serial(args.serial, args.baudrate, timeout=1) as ser:
        print(f"Listening on {args.serial} at {args.baudrate} baud...")

        LED = LEDLang(ser)
        LED.set_folder(args.folder)
        LED.playfile(args.animation) 