import os
import time

from volume_controller.controller import AudioController

controller = AudioController()

ASSETS_FOLDER = "assets"
controller.send_icon(0, os.path.join(ASSETS_FOLDER, "test.png"))
controller.send_volume(0, 99)
time.sleep(10)
