from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("tap-canvas")
except PackageNotFoundError:
    try:
        __version__ = version("tap-canvas-blank")
    except PackageNotFoundError:
        __version__ = "0.0.6"