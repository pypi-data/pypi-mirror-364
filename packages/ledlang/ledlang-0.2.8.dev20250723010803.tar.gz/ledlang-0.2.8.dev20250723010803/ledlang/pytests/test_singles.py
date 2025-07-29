import threading
import time
from ledlang import PytestLEDDeviceSimulator, LEDLang

def newDevice(size="3x3"):
    simulator = PytestLEDDeviceSimulator(size)
    threading.Thread(target=simulator.run, daemon=True).start()
    ledlang = LEDLang(serial_obj=simulator.serial)
    return simulator, ledlang

def test_line():
    simulator, ledlang = newDevice()

    ledlang.play(ledlang.compile("""
    INIT 3x3
    LINE 0 0 1 0
    LINE 0 1 2 1
    LINE 0 2 1 2
    """))

    time.sleep(0.05)

    assert simulator.kill() == [
        [1, 1, 0],
        [1, 1, 1],
        [1, 1, 0],
    ]

def test_plot():
    simulator, ledlang = newDevice()

    ledlang.play(ledlang.compile("""
    INIT 3x3
    PLOT 0 0
    PLOT 1 1
    PLOT 2 2
    """))

    time.sleep(0.05)

    assert simulator.kill() == [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]

#def test_rotate():
#    simulator, ledlang = newDevice()
#
#    ledlang.play(ledlang.compile("""
#    INIT 3x3
#    ROTATE 90
#    PLOT 0 0
#    PLOT 1 1
#    PLOT 2 2
#    """))
#
#    time.sleep(0.05)
#
#    assert simulator.kill() == [
#        [0, 0, 1],
#        [0, 1, 0],
#        [1, 0, 0],
#    ]