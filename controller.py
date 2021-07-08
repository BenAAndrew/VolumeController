import serial
import time
import imageio

VOLUME_STEP = 0.02
MINIMUM_OPACITY = 200
BAUDRATE = 19200
TIMEOUT = 0.1


class AudioController:
    def __init__(self):
        for i in range(2, 10):
            try:
                self.serial = serial.Serial(f"COM{i}", BAUDRATE, timeout=TIMEOUT)
                time.sleep(5)
                break
            except:
                print(f"Could not connect to COM{i}")

    def is_done(self):
        return self.serial.read() == b'd'

    def send_icon(self, position, icon_path):
        self.serial.write(b'i')
        image = imageio.imread(icon_path)
        pixels = [tuple(p[:3]) if p[3] >= MINIMUM_OPACITY else (0,0,0) for row in image for p in row]
        colours = list(set(pixels))
        self.serial.write(bytes([position, len(colours)]))

        for colour in colours:
            self.serial.write(bytes(colour))

        for pixel in pixels:
            self.serial.write(bytes([colours.index(pixel)]))

        while not self.is_done():
            pass

    def send_volume(self, position, volume):
        self.serial.write(b'v')
        self.serial.write(bytes([position, volume]))
        while not self.is_done():
            pass

    def update(self, master_audio, apps):
        data = int.from_bytes(self.serial.read(), "big")
        if data > 0:
            index = data // 10
            code = data % 10

            if index == 0:
                app = master_audio
            else:
                app = apps[index-1]

            # Anti-clockwise
            if code == 1:
                app.change_volume(-VOLUME_STEP)
            # Clockwise
            elif code == 2:
                app.change_volume(VOLUME_STEP)
            # Press
            elif code == 3:
                pass

    def close(self):
        self.serial.close()
