from requests.exceptions import Timeout
from main import CONFIG, DB
import requests

def register(localpart: str):
    resp = requests.get(f"http://{CONFIG['homeserver']}",timeout=10)
    resp.raise_for_status()
    DB.table("users").insert({
        "id": resp.json()["user_id"],
        "token": resp.json()["access_token"],
        "device": resp.json()["device_id"]
    })