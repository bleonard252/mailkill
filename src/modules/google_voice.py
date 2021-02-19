import json
import requests
from datetime import datetime
from requests.api import request
from tinydb.queries import Query, where
from src.matrix_src.asuser import sendFromUserToRoom
from src.matrix_src import requesthelper
from src.matrix_src.appservice_register import register_room, register_user
import src.config as config
from mailparser import MailParser
from src.addressconverter import *
import re

def nullFunc(*args, **kwargs):
    pass

def on_email(email: MailParser, **kwargs):
    markAsRead = nullFunc
    fromAddr = email.from_[0][1]
    if kwargs.__contains__("markAsRead"):
        markAsRead = kwargs["markAsRead"]
    #print(email.body)
    smsregex = re.match(r'^<https://voice\.google\.com>[\r\n]+(?P<sms>.*?)[\r\n]+(?:YOUR ACCOUNT|To respond to this text message, )', email.body, re.DOTALL)
    addrregex = re.match(r'^(?P<mynum>\d+?)\.(?P<othernum>\d+?)\.(?P<random>.*?)\@txt.voice.google.com$', fromAddr)
    smscontent = ""
    if (smsregex is not None): smscontent = smsregex.group('sms')
    # Debug log
    print(f"""Got new text message!\n
From: {addrregex.group('othernum')}\n
{smscontent}""")
    roomname = "mailkill_google-voice_"+addrregex.group('othernum')
    # Interact with the database, prepare user, room
    if not config.DATABASE.table("users").contains(where("email") == fromAddr):
        register_user(email_to_localpart(fromAddr), fromAddr, name="+"+addrregex.group('othernum'))
    usertoken = config.DATABASE.table("users").get(where("email") == fromAddr).get("token")
    if not config.DATABASE.table("rooms").contains(where("email") == fromAddr):
        register_room(roomname, fromAddr, name="+"+addrregex.group('othernum')+" (SMS)")
        roomid = config.DATABASE.table("rooms").get(where("email") == fromAddr).get("id")
        invresp = requests.post(f"http://{config.CONFIG['homeserver_url']}/_matrix/client/r0/rooms/{roomid}/invite",
            json={"user_id": f"@{email_to_localpart(fromAddr)}:{config.CONFIG['homeserver']}"},
            timeout=10, auth=requesthelper.BearerAuth(config.CONFIG["access_token"])
        )
        joinresp = requests.post(f"http://{config.CONFIG['homeserver_url']}/_matrix/client/r0/join/{roomid}",
            timeout=10, auth=requesthelper.BearerAuth(usertoken)
        )
        invresp.raise_for_status()
        joinresp.raise_for_status()
    roomid = config.DATABASE.table("rooms").get(where("email") == fromAddr).get("id")
    # Send to Matrix
    # if len(email.text_not_managed) > 0:
    #     for attachment in email.text_not_managed:
    #         if attachment.startswith("\xff\xd8\xff\xe0\x10JFIF"):
    #             fn = datetime.now().timestamp().__trunc__()
    #             open(f"/tmp/{fn}.jpeg", "wb+").write(attachment)
    #             with open(f"/tmp/{fn}.jpeg", "rb") as fobj:
    #                 attresp = requests.post(f"http://{config.CONFIG['homeserver_url']}/_matrix/media/r0/upload",
    #                     data=attachment, headers={"Content-Type": "image/jpeg"},
    #                     timeout=10, auth=requesthelper.BearerAuth(usertoken))
    #                 attresp.raise_for_status()
    #             resp = requests.put(f"http://{config.CONFIG['homeserver']}/_matrix/client/r0/rooms/{roomid}/send/m.room.message/99{datetime.now().timestamp().__trunc__()}88",
    #                 json={"url":attresp.json()["content_uri"], "body": "image.jpeg", "msgtype": "m.image"},
    #                 timeout=10, auth=requesthelper.BearerAuth(usertoken)
    #             )
    #             resp.raise_for_status()
    # TODO: re-add attachments. https://github.com/SpamScope/mail-parser/issues/70 is required for this to work
    sendFromUserToRoom(f"@{email_to_localpart(fromAddr)}:{config.CONFIG['homeserver']}", roomid, usertoken, content={"body": smscontent, "msgtype": "m.text"})
    # Finally, mark as read (to prevent parsing it again)
    markAsRead(email)