import os
import shutil
from unittest import mock
import imageio

from volume_controller.fetch_icon import fetch_icon


ICONS_FOLDER = "icons"


@mock.patch("volume_controller.fetch_icon.IconExtractor")
def test_fetch_icon(iconExtractor):
    path = os.path.join("icons", "icon-simple.png")
    os.makedirs(ICONS_FOLDER, exist_ok=True)
    if os.path.isfile(path):
        os.remove(path)
    shutil.copyfile(os.path.join("assets", "icon.png"), os.path.join("icons", "icon.png"))

    fetch_icon("fake_path", "icon")

    assert os.path.isfile(path)
    image = imageio.imread(path)
    pixels = [tuple(p[:3]) for row in image for p in row]
    colours = list(set(pixels))
    assert len(colours) == 30
