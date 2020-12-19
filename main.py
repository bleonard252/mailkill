import argparse
import nio
import os, sys, json
import src.matrix
import tinydb

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

_CONFIG = None
if args.config != "":
    _CONFIG = open(args.config).read()
elif os.environ.__contains__("MAILKILL_CONFIG"):
    _CONFIG = open(os.environ["MAILKILL_CONFIG"]).read()
elif os.path.exists("~/.config/mailkill.json"):
    _CONFIG = open("~/.config/mailkill.json").read()
elif os.path.exists("/etc/mailkill.json"):
    _CONFIG = open("/etc/mailkill.json").read()
elif os.path.exists("./mailkill.json"):
    _CONFIG = open("./mailkill.json").read()
else:
    os.error("FATAL: No config exists!")
    exit(1)
CONFIG = json.loads(_CONFIG)
globals()["CONFIG"] = CONFIG

# =========================
# == INITIALIZE DATABASE ==
# =========================
DB = tinydb.TinyDB(CONFIG["database"])
globals()["DATABASE"] = DB

# =================
# == USE MODULES ==
# =================
if args.google_voice:
    print("Using Google Voice")


# =========================
# == INITIALIZE SERVICES ==
# =========================
if __name__ == "__main__":
    #mxclient = nio.AsyncClient(CONFIG["homeserver"])
    #if DB.table("client").contains(tinydb.Query().access_token):
    src.matrix.app.run(port=CONFIG["port"] | 46666 )