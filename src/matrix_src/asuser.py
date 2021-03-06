from datetime import datetime
import json
from os import urandom
from typing import Mapping
from requests.exceptions import Timeout
from src import config
import requests
from . import requesthelper

def sendFromUserToRoom(fromUser: str, toRoom: str, fromToken: str, evtype: str = "m.room.message", content: Mapping = {}): 
    """
    Send an event to a room.
    """
    CONFIG = config.CONFIG
    resp = requests.put(f"http://{CONFIG['homeserver']}/_matrix/client/r0/rooms/{toRoom}/send/{evtype}/99{datetime.now().timestamp().__trunc__()}88",
        json.dumps(content),
        timeout=10, auth=requesthelper.BearerAuth(fromToken)
    )
    resp.raise_for_status()
    return True