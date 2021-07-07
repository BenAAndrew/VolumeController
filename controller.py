import serial
import time
import imageio

class AudioController:
    def __init__(self):
        for i in range(2, 10):
            try:
                self.serial = serial.Serial(f"COM{i}", 9600, timeout=1)
                time.sleep(5)
                break
            except:
                print(f"Could not connect to COM{i}")

    def is_done(self):
        return self.serial.read() == b'd'

    def send_icon(self, position, icon_path):
        self.serial.write(b'i')
        self.serial.write(bytes([position]))
        image = imageio.imread(icon_path)
        for row in image:
            self.serial.write(bytes(row))
        while not self.is_done():
            pass

    def send_volume(self, position, volume):
        self.serial.write(b'v')
        self.serial.write(bytes([position, volume]))
        while not self.is_done():
            pass

    def close(self):
        self.serial.close()
