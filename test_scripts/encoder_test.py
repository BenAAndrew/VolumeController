import serial
import time

serial = serial.Serial("COM3", 9600, timeout=0.1)
time.sleep(5)

while True:
    print(int.from_bytes(serial.read(), "big"))
