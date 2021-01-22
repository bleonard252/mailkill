import json
from requests.exceptions import Timeout
from main import CONFIG, DB
import requests
from . import requesthelper

def register_user(localpart: str, correspondsTo: str):
    """
    Create a Matrix user.
    """
    resp = requests.post(f"http://{CONFIG['homeserver_url']}/_matrix/client/r0/register", 
        json.dumps({"type": "m.login.application_service", "username": localpart}),
        timeout=10, auth=requesthelper.BearerAuth(CONFIG["access_token"])
    )
    nickresp = requests.post(f"http://{CONFIG['homeserver_url']}/_matrix/client/r0/profile/@{localpart}:{CONFIG['homeserver']}/displayname", 
        json.dumps({"displayname": correspondsTo}),
        timeout=10, auth=requesthelper.BearerAuth(CONFIG["access_token"])
    )
    #print(resp.json()) # DEBUG
    resp.raise_for_status()
    nickresp.raise_for_status()
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
    resp = requests.post(f"http://{CONFIG['homeserver_url']}/_matrix/client/r0/createRoom", 
        json.dumps({"room_alias_name": localpart, "creation_content": {"io.github.bleonard252.mailkill.email": correspondsTo}, "preset": "private_chat", **kwargs}),
        timeout=10, auth=requesthelper.BearerAuth(CONFIG["access_token"])
    )
    invresp = requests.post(f"http://{CONFIG['homeserver_url']}/_matrix/client/r0/rooms/{resp.json()['room_id']}/invite", 
        json.dumps({"user_id": CONFIG['end_user'], **kwargs}),
        timeout=10, auth=requesthelper.BearerAuth(CONFIG["access_token"])
    )
    resp.raise_for_status()
    invresp.raise_for_status()
    DB.table("rooms").insert({
        "id": resp.json()["room_id"],
        "alias": "#"+localpart+":"+CONFIG["homeserver"],
        "email": correspondsTo,
    })