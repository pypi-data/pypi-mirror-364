import threading
from ledlang import PytestLEDDeviceSimulator, LEDLang

def newDevice(size="3x3"):
    simulator = PytestLEDDeviceSimulator(size)
    threading.Thread(target=simulator.run, daemon=True).start()
    ledlang = LEDLang(serial_obj=simulator.serial, wait=False)
    return simulator, ledlang

def test_line():
    simulator, ledlang = newDevice()

    ledlang.play(ledlang.compile("""
    INIT 3x3
    LINE 0 0 1 0
    LINE 0 1 2 1
    LINE 0 2 1 2
    """))
    assert simulator.kill() == [
        [1, 1, 0],
        [1, 1, 1],
        [1, 1, 0],
    ]