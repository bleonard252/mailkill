import email, imaplib
import mailparser
from tinydb import Query, where
import yagmail
import asyncio
from main import CONFIG, DB

async def listen():
    # some of the code below shamelessly stolen from the Internet
    client = imaplib.IMAP4_SSL(CONFIG["imap_server"])
    client.login(CONFIG["imap_username"], CONFIG["imap_password"])
    client.print_log()
    client.select('inbox')
    async def inner():
        status, data = client.search(None, 'ALL') # get all messages
        mail_ids = []
        for block in data:
            mail_ids += block.split()
        inbox = []
        for mail_id in mail_ids:
            result, data = client.fetch(mail_id, "(RFC822)")
            inbox += mailparser.parse_from_bytes(data)
        latest_email = DB.table
        prev_email = DB.table("client").get(where("latest_message_date").exists())["latest_message_date"]
        DB.table("client").upsert({
            "latest_message_date": email.date
        }, where("latest_message_date").exists())
        if prev_email != email.date: # new message!
            # filter down to new emails
            assert inbox[-1] != prev_email
            unread = []
            for email in inbox.__reversed__():
                if email.date == prev_email.date:
                    break
                else:
                    unread += email
            for email in unread:
                print(email)
                # TODO: do something with the email
    while True:
        await asyncio.run(inner())
        await asyncio.sleep(5)