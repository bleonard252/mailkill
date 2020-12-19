"""
The Matrix module for Mailkill.
"""
from flask.globals import request
from flask.json import jsonify
from flask.wrappers import Response
import nio
import flask

app = flask.app.Flask(__name__)

@app.route("/transactions/<transaction>", methods=["PUT"])
def on_receive_events(transaction):
    # Check token
    if request.authorization == None:
        flask.abort(Response('"errcode": "IO.GITHUB.BLEONARD252.MAILKILL_UNAUTHORIZED",'
        '"error": "Mailkill requires a correct Homeserver token"}', 401))
    elif request.authorization != globals()["CONFIG"]["service_token"]:
        flask.abort(Response('"errcode": "IO.GITHUB.BLEONARD252.MAILKILL_FORBIDDEN",'
        '"error": "Mailkill requires a correct Homeserver token"}', 403))
    # Process events
    events = request.get_json()["events"]
    for event in events:
        # This will be super useful once events start coming in:
        # print("User: %s Room: %s" % (event["user_id"], event["room_id"]))
        # print("Event Type: %s" % event["type"])
        # print("Content: %s" % event["content"])
        pass
    return jsonify({})

