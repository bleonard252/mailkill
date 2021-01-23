from argparse import Namespace
import os, json

from tinydb.database import TinyDB

def init(args: Namespace):
    _CONFIG = None
    if args.__contains__("config"):
        _CONFIG = open(args.config).read()
    elif os.environ.__contains__("MAILKILL_CONFIG"):
        _CONFIG = open(os.environ["MAILKILL_CONFIG"]).read()
    elif os.path.exists("~/.config/mailkill.json"):
        _CONFIG = open("~/.config/mailkill.json").read()
    elif os.path.exists("/etc/mailkill.json"):
        _CONFIG = open("/etc/mailkill.json").read()
    elif os.path.exists("./config.json"):
        _CONFIG = open("./config.json").read()
    else:
        print("FATAL: No config exists!")
        exit(1)
    global CONFIG
    CONFIG = json.loads(_CONFIG)
    global DATABASE
    if not os.path.exists(CONFIG["database"]):
        os.system("echo {} > "+CONFIG['database'])
    DATABASE = TinyDB(CONFIG["database"])
    global ARGS
    ARGS = args