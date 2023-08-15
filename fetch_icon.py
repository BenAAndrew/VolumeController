import os
from PIL import Image
from icoextract import IconExtractor

ICONS_FOLDER = "icons"
ICON_SIZE = 60
MAX_COLOURS = 30


def get_icon(app_path: str, name: str) -> str:
    icon_path = os.path.join(ICONS_FOLDER, name + "-simple.png")

    if not os.path.isfile(icon_path):
        extractor = IconExtractor(app_path)
        extractor.export_icon(icon_path)
        icon = Image.open(icon_path).resize((ICON_SIZE, ICON_SIZE), Image.ANTIALIAS)
        icon.quantize(MAX_COLOURS).save(icon_path)

    return icon_path
