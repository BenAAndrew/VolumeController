import os
import serial
import imageio
import time

serial = serial.Serial("COM3", 9600, timeout=1)
time.sleep(5)

def is_done():
    return serial.read() == b'd'

def send_icon(icon_path):
    image = imageio.imread(icon_path)
    for row in image:
        serial.write(bytes(row))
    while not is_done():
        pass
    print("BITMAP DRAWN")

def send_text(text):
    serial.write(str.encode(text))
    while not is_done():
        pass
    print("TEXT DRAWN")

send_icon("icon.bmp")
send_text("Hello")
send_icon(os.path.join("icons", "steam.bmp"))
