from requests.exceptions import Timeout
from main import CONFIG, DB
import requests
from . import requesthelper

def register_user(localpart: str, correspondsTo: str):
    """
    Create a Matrix user.
    """
    resp = requests.get(f"http://{CONFIG['homeserver']}/_matrix/client/r0/register", 
        {"type": "m.login.application_service", "username": localpart},
        timeout=10, auth=requesthelper.BearerAuth(CONFIG["access_token"])
    )
    resp.raise_for_status()
    DB.table("users").insert({
        "id": resp.json()["user_id"],
        "token": resp.json()["access_token"],
        "device": resp.json()["device_id"],
        "email": correspondsTo
    })
def register_room(localpart: str, correspondsTo: str, **kwargs):
    """
    Create a new room with a localpart and other things.
    You can set name="", is_direct=true, and other
    keys listed in the Matrix room creation API.
    """
    resp = requests.get(f"http://{CONFIG['homeserver']}/_matrix/client/r0/createRoom", 
        {"room_alias_name": localpart, **kwargs},
        timeout=10, auth=requesthelper.BearerAuth(CONFIG["access_token"])
    )
    resp.raise_for_status()
    DB.table("rooms").insert({
        "id": resp.json()["room_id"],
        "email": correspondsTo,
    })