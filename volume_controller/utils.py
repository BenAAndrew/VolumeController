import os
import sys


def resource(relative_path):
    base_path = getattr(sys, "_MEIPASS", None)
    return os.path.join(base_path, relative_path) if base_path else relative_path
