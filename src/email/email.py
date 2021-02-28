import email as elib, imaplib
import mailparser
from mailparser.mailparser import MailParser
from tinydb import Query, where
import yagmail
import asyncio
import src.config
import datetime
from signal import signal, SIGTERM
import src.modules.google_voice as GoogleVoice
from src import config

CONTINUE: bool = True

def listen():
    CONFIG = src.config.CONFIG
    DB = src.config.DATABASE
    # some of the code below shamelessly stolen from the Internet
    client = imaplib.IMAP4_SSL(CONFIG["imap_server"])
    client.login(CONFIG["imap_username"], CONFIG["imap_password"])
    client.select('inbox')
    async def inner():
        if CONFIG["imap_server"] == "imap.gmail.com":
            status, data = client.search(None, 'X-GM-RAW "in:unread"') # get all messages
        else:
            status, data = client.search(None, 'UnSeen') # get all messages
        mail_ids = []
        for block in data:
            mail_ids += block.split()
        inbox = []
        if len(mail_ids) == 0: return
        for mail_id in mail_ids:
            result, data = client.fetch(mail_id, "BODY.PEEK[]")
            #client.store(mail_id,"-FLAGS", '\Seen')
            inbox.append(mailparser.parse_from_bytes(data[0][1]))
        latest_email = inbox[-1]
        if DB.table("client").get(where("latest_message_date").exists()) == None:
            #datetime.date().isoformat()
            DB.table("client").insert({"latest_message_date": latest_email.date.timestamp()})
        prev_email = DB.table("client").get(where("latest_message_date").exists())["latest_message_date"]
        DB.table("client").upsert({
            "latest_message_date": latest_email.date.timestamp()
        }, where("latest_message_date").exists())
        def markAsRead(mailParser: MailParser):
            mail_id = mail_ids[inbox.index(mailParser)]
            client.store(mail_id,"+FLAGS", '\Seen')
        for email in inbox:
            if email.from_[0][1].endswith("@txt.voice.google.com") and config.ARGS.google_voice == True:
                GoogleVoice.on_email(email, markAsRead=markAsRead)
    while CONTINUE:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(inner())
        loop.run_until_complete(asyncio.sleep(5))
def _sigterm(_1=None, _2=None):
    CONTINUE = False
signal(SIGTERM, _sigterm)

