__version__ = '0.0.1.dev22'

try:
    from importlib.metadata import version
    __version__ = version("solidkit")
except:
    pass
