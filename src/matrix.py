"""
The Matrix module for Mailkill.
"""
import json
from os import name
import requests
from tinydb.queries import where
from src.matrix_src import asuser
from src import config
from flask.globals import request
from flask.json import jsonify
from flask.wrappers import Response
from jinja2.utils import urlize
import nio
import flask
from tinydb import TinyDB, Query
import re
from urllib.parse import unquote
import yagmail
from src.matrix_src import requesthelper
#import matrix_src as mx

# ==================================
# == INITIALIZE APP AND CONSTANTS ==
# ==================================

app = flask.app.Flask(__name__)
malformedid = Response('"errcode": "IO.GITHUB.BLEONARD252.MAILKILL_MALFORMED",'
    '"error": "The ID given is not valid for Mailkill"}', 404)
unauthorized = Response('"errcode": "IO.GITHUB.BLEONARD252.MAILKILL_UNAUTHORIZED",'
    '"error": "Mailkill requires a correct Homeserver token"}', 401)
forbidden = Response('"errcode": "IO.GITHUB.BLEONARD252.MAILKILL_FORBIDDEN",'
    '"error": "Mailkill requires a correct Homeserver token"}', 403)
notfound = Response('"errcode": "IO.GITHUB.BLEONARD252.MAILKILL_NOT_FOUND",'
    '"error": "The entity does not exist, probably because Mailkill hasn\'t recieved '
    'a message from the associated address."}', 404)

# ===================
# == API ENDPOINTS ==
# ===================

@app.route("/_matrix/app/v1/transactions/<transaction>", methods=["PUT"])
@app.route("/transactions/<transaction>", methods=["PUT"])
def on_receive_events(transaction):
    DB = config.DATABASE
    CONFIG = config.CONFIG
    # Check token
    if request.authorization == None and request.args.get("access_token", type=str) == None:
        flask.abort(unauthorized)
    elif request.authorization != CONFIG["service_token"] and request.args.get("access_token", type=str) != CONFIG["service_token"]:
        flask.abort(forbidden)
    # Process events
    events = request.get_json()["events"]
    for event in events:
        # This will be super useful once events start coming in:
        # print("User: %s Room: %s" % (event["user_id"], event["room_id"]))
        # print("Event Type: %s" % event["type"])
        # print("Content: %s" % event["content"])
        # Here, you will interpret the ID to determine which module to
        # send the message to, and if the module is active.
        emailaddr = DB.table("rooms").get(where("id") == event["room_id"]).get("email")
        # client = smtplib.IMAP4_SSL(CONFIG["imap_server"])
        # client.login(CONFIG["imap_username"], CONFIG["imap_password"])
        # client.
        if event["user_id"] == CONFIG["end_user"]:
            #yagmail.register(CONFIG["imap_username"], CONFIG["imap_password"])
            client = yagmail.SMTP(CONFIG["imap_username"], CONFIG["imap_password"], CONFIG["smtp_server"])
            client.login()
            if event["type"] == "m.room.message" and event["content"].__contains__("msgtype") and event["content"]["msgtype"] == "m.text":
                if event["content"]["body"].startswith(CONFIG["prefix"]):
                    split = event["content"]["body"].split(" ")
                    if split[0] == CONFIG["prefix"]+"nickname":
                        newNick = event["content"]["body"].replace(CONFIG["prefix"]+"nickname ", "")
                        usertonick = DB.table("users").get(where("email") == DB.table("rooms").get(where("id") == event["room_id"]).get("email"))
                        nickresp = requests.put(f"http://{CONFIG['homeserver_url']}/_matrix/client/r0/profile/{usertonick.get('id')}/displayname", 
                            json.dumps({"displayname": newNick}),
                            timeout=10, auth=requesthelper.BearerAuth(usertonick.get("token"))
                        )
                        moduleIdentifier = " (Mailkill)"
                        if usertonick.get("email").endswith("@txt.voice.google.com") and config.ARGS.google_voice == True:
                            moduleIdentifier = " (SMS)"
                        nameresp = requests.put(f"http://{CONFIG['homeserver_url']}/_matrix/client/r0/rooms/{event['room_id']}/state/m.room.name", 
                            json.dumps({"name": newNick + moduleIdentifier}),
                            timeout=10, auth=requesthelper.BearerAuth(CONFIG["access_token"])
                        )
                        nickresp.raise_for_status()
                        nameresp.raise_for_status()
                    elif split[0] == CONFIG["prefix"]+"avatar":
                        newAvatar = event["content"]["body"].replace(CONFIG["prefix"]+"avatar ", "")
                        usertonick = DB.table("users").get(where("email") == DB.table("rooms").get(where("id") == event["room_id"]).get("email"))
                        avresp = requests.put(f"http://{CONFIG['homeserver_url']}/_matrix/client/r0/profile/{usertonick.get('id')}/avatar_url", 
                            json.dumps({"avatar_url": newAvatar}),
                            timeout=10, auth=requesthelper.BearerAuth(usertonick.get("token"))
                        )
                        roomresp = requests.put(f"http://{CONFIG['homeserver_url']}/_matrix/client/r0/rooms/{event['room_id']}/state/m.room.avatar", 
                            json.dumps({"url": newAvatar}),
                            timeout=10, auth=requesthelper.BearerAuth(CONFIG["access_token"])
                        )
                        avresp.raise_for_status()
                        roomresp.raise_for_status()
                    elif split[0] == CONFIG["prefix"]+"ping":
                        asuser.sendFromUserToRoom(CONFIG["mailkill_bot"], event["room_id"], CONFIG["access_token"],
                        content={
                            "body": f"Pong! {event['user_id']}",
                            "msgtype": "m.notice"
                        })
                    elif split[0] == CONFIG["prefix"]+"help":
                        asuser.sendFromUserToRoom(CONFIG["mailkill_bot"], event["room_id"], CONFIG["access_token"],
                        content={
                            "body": f"""Mailkill help\n"""
                            f"""{CONFIG["prefix"]}help : Show this help message\n"""
                            f"""{CONFIG["prefix"]}nickname : Set the nickname of the email target\n"""
                            f"""{CONFIG["prefix"]}avatar : Set the avatar of the email target (requires MXC URL)\n"""
                            """\n---""",
                            "msgtype": "m.notice"
                        })
                    else: 
                        asuser.sendFromUserToRoom(CONFIG["mailkill_bot"], event["room_id"], CONFIG["access_token"],
                        content={
                            "body": f"Command {split[0]} not found",
                            "msgtype": "m.notice"
                        })
                    pass
                else:
                    client.send(to=emailaddr, contents=event["content"]["body"])
                    print("Non-command message received. Message bridged.")
        pass
    return jsonify({})

@app.route("/_matrix/app/v1/users/<userId>", methods=["GET"])
def on_query_user_exists(userid: str):
    DB = config.DATABASE
    CONFIG = config.CONFIG
    # Check token
    if request.authorization == None:
        flask.abort(unauthorized)
    elif request.authorization != CONFIG["service_token"]:
        flask.abort(forbidden)
    # Check if user ID is valid
    elif re.match(r'\@mailkill_[a-z0-9.-_]+\:.+', unquote(userid)) == None:
        flask.abort(malformedid)
    # Check if user exists
    elif not DB.table("users").contains(Query().id == userid):
        flask.abort(notfound)
    #globals()["DATABASE"].table("users").get(Query().id == userid)
    return jsonify({})