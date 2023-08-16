import os
from PIL import Image
from icoextract import IconExtractor

ICONS_FOLDER = "icons"
ICON_SIZE = 60
MAX_COLOURS = 30


def get_icon(app_path: str, name: str) -> str:
    download_path = os.path.join(ICONS_FOLDER, name + ".png")
    simplified_path = os.path.join(ICONS_FOLDER, name + "-simple.png")

    if not os.path.isfile(simplified_path):
        extractor = IconExtractor(app_path)
        extractor.export_icon(download_path)
        icon = Image.open(download_path).resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
        icon.quantize(MAX_COLOURS).save(simplified_path)

    return simplified_path
