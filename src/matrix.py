"""
The Matrix module for Mailkill.
"""
from flask.globals import request
from flask.json import jsonify
from flask.wrappers import Response
from jinja2.utils import urlize
import nio
import flask
from tinydb import TinyDB, Query
import re
from urllib.parse import unquote
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
def on_receive_events(transaction):
    # Check token
    if request.authorization == None:
        flask.abort(unauthorized)
    elif request.authorization != globals()["CONFIG"]["service_token"]:
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
        pass
    return jsonify({})

@app.route("/_matrix/app/v1/users/<userId>", methods=["GET"])
def on_query_user_exists(userid: str):
    # Check token
    if request.authorization == None:
        flask.abort(unauthorized)
    elif request.authorization != globals()["CONFIG"]["service_token"]:
        flask.abort(forbidden)
    # Check if user ID is valid
    elif re.match(r'\@mailkill_[a-z0-9.-_]+\:.+', unquote(userid)) == None:
        flask.abort(malformedid)
    # Check if user exists
    elif not globals()["DATABASE"].table("users").contains(Query().id == userid):
        flask.abort(notfound)
    #globals()["DATABASE"].table("users").get(Query().id == userid)
    return jsonify({})