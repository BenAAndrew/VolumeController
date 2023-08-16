from dataclasses import dataclass
from enum import Enum
import serial
import time
import imageio

BAUDRATE = 14400
TIMEOUT = 0.1


class ControlEventType(Enum):
    VOLUME_UP = 0
    VOLUME_DOWN = 1
    TOGGLE_MUTE = 2


@dataclass
class ControlEvent:
    event_type: ControlEventType
    app_index: int


class AudioController:
    serial = None

    def __init__(self):
        for i in range(2, 10):
            try:
                self.serial = serial.Serial(f"COM{i}", BAUDRATE, timeout=TIMEOUT)
                time.sleep(5)
                break
            except:
                pass
        assert self.serial, "Could not connect"

    def wait_for_success(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            while not args[0].serial.read() == b'd':
                print("ALIVE", time.time())
                # pass
        return wrapper

    # Arduino interactions
    @wait_for_success
    def send_icon(self, position, icon_path):
        self.serial.write(b'i')
        image = imageio.imread(icon_path)
        pixels = [tuple(p[:3]) for row in image for p in row]
        colours = list(set(pixels))
        self.serial.write(bytes([position, len(colours)]))

        for colour in colours:
            self.serial.write(bytes(colour))

        for pixel in pixels:
            self.serial.write(bytes([colours.index(pixel)]))

    @wait_for_success
    def send_volume(self, position, volume):
        self.serial.write(b'v')
        self.serial.write(bytes([position, volume]))

    @wait_for_success
    def mute_app(self, position):
        self.serial.write(b'm')
        self.serial.write(bytes([position]))

    @wait_for_success
    def delete_app(self, position):
        self.serial.write(b'd')
        self.serial.write(bytes([position]))

    def poll(self):
        data = int.from_bytes(self.serial.read(), "big")
        if data > 0:
            index = data // 10
            code = data % 10
            event_type = None
            
            # Anti-clockwise
            if code == 1:
                event_type = ControlEventType.VOLUME_DOWN
            # Clockwise
            elif code == 2:
                event_type = ControlEventType.VOLUME_UP
            # Press
            elif code == 3:
                event_type = ControlEventType.TOGGLE_MUTE

            if event_type is not None:
                return ControlEvent(event_type, index)

    def close(self):
        self.serial.close()
