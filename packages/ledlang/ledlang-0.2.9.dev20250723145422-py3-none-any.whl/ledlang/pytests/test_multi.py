import os
import pty
import serial
import threading
from ledlang import MultiLEDLang, PytestLEDDeviceSimulator

def test_multisides():
    simulator1 = PytestLEDDeviceSimulator("3x3")
    simulator2 = PytestLEDDeviceSimulator("3x3")
    threading.Thread(target=simulator1.run, daemon=True).start()
    threading.Thread(target=simulator2.run, daemon=True).start()
    displays = {
        'size': '3x3',
        'displays': [
            {
                'serial': simulator1.serial,
                'rotation': 0
            },
            {
                'serial': simulator2.serial,
                'rotation': 0
            },
        ]
    }
    multi = MultiLEDLang(displays)
    multi.play(multi.compile("""
    INIT 6x3
    DISPLAY [
    1 1 0 0 1 1
    1 1 0 0 1 1
    1 1 0 0 1 1
    ]
    """))
    assert simulator1.kill() == [
        [1, 1, 0],
        [1, 1, 0],
        [1, 1, 0],
    ]
    assert simulator2.kill() == [
        [0, 1, 1],
        [0, 1, 1],
        [0, 1, 1],
    ]

def test_multichess():
    simulator1 = PytestLEDDeviceSimulator("3x3")
    simulator2 = PytestLEDDeviceSimulator("3x3")
    threading.Thread(target=simulator1.run, daemon=True).start()
    threading.Thread(target=simulator2.run, daemon=True).start()
    displays = {
        'size': '3x3',
        'displays': [
            {
                'serial': simulator1.serial,
                'rotation': 0
            },
            {
                'serial': simulator2.serial,
                'rotation': 0
            },
        ]
    }
    multi = MultiLEDLang(displays)
    multi.play(multi.compile("""
    INIT 6x3
    DISPLAY [
    0 1 0 1 0 1
    1 0 1 0 1 0
    0 1 0 1 0 1
    ]
    """))
    assert simulator1.kill() == [
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0],
    ]
    assert simulator2.kill() == [
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1],
    ]