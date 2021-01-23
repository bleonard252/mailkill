import argparse
import nio
import os, sys, json, asyncio, signal
from multiprocessing import Process
import src.matrix
import tinydb
import src.email.email as email
from src import config

globals()["CONTINUE"] = True

# ================
# == PARSE ARGS ==
# ================
args__parser = argparse.ArgumentParser(description='A Matrix email to conversation bridge.')
args__parser.add_argument('--google-voice', action='store_true',
    help="""Enable the Google Voice text message module.
    In order to use it, you must configure Voice to forward text messages to your email address.""")
args__parser.add_argument('-c, --config', type=str, default="", metavar="FILE",
    help="""Specify a config file. This file stores API keys. You can also set the configuration
    in ~/.config/mailkill.json, /etc/mailkill.json, ./mailkill.json or the pathname in the
    MAILKILL_CONFIG environment variable.""")

args = args__parser.parse_args()
globals()["ARGS"] = args

# =================
# == LOAD CONFIG ==
# =================
config.init(args)
CONFIG = config.CONFIG

#globals()["CONFIG"] = CONFIG

# =========================
# == INITIALIZE DATABASE ==
# =========================
DB = config.DATABASE

# =================
# == USE MODULES ==
# =================
if args.google_voice == True:
    print("Using Google Voice")

# =========================
# == INITIALIZE SERVICES ==
# =========================
TASK = None; SERVER = None
if __name__ == "__main__":
    #mxclient = nio.AsyncClient(CONFIG["homeserver"])
    #if DB.table("client").contains(tinydb.Query().access_token):
    #TASK = asyncio.create_task(email.listen())
    #TASK = Process(target=email.listen)
    SERVER = Process(target=src.matrix.app.run,
        kwargs={"host": "0.0.0.0", "port": CONFIG["port"], "debug": False})
    SERVER.start()
    print(f"Web server started on port {CONFIG['port']}")
    email.listen()
def _sigterm():
    print("Terminating Mailkill gracefully...")
    globals()["CONTINUE"] = False
    SERVER.terminate()
signal.signal(signal.SIGTERM, _sigterm)