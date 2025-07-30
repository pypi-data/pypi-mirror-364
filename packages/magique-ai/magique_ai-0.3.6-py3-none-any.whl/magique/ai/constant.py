import os

_SEP = "|"
DEFAULT_MAGIQUE_SERVER_URL = (
    f"ws://server.magique1.aristoteleo.com/ws{_SEP}"
    f"ws://server.magique2.aristoteleo.com/ws{_SEP}"
    f"ws://magique.heartst.aristoteleo.com/ws{_SEP}"
    f"ws://magique.spateo.aristoteleo.com/ws{_SEP}"
    f"ws://magique3.aristoteleo.com/ws"
)

_SERVER_URL = os.environ.get("MAGIQUE_SERVER_URL", DEFAULT_MAGIQUE_SERVER_URL)

SERVER_URLS = []
if _SEP in _SERVER_URL:
    SERVER_URLS = _SERVER_URL.split(_SEP)
else:
    SERVER_URLS = [_SERVER_URL]
