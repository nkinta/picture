
import socket
host = socket.gethostname()
# cf = __import__("", fromlist=("config_{}".format(host.lower()),))

import importlib
cf = importlib.import_module("config_{}".format(host.lower()))

__all__ = ["cf"]