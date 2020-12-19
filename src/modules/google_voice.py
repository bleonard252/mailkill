import src.config as config
from mailparser import MailParser
import re

def nullFunc():
    pass

def on_email(email: MailParser, **kwargs):
    markAsRead = nullFunc
    if kwargs.__contains__("markAsRead"):
        markAsRead = kwargs["markAsRead"]
    #print(email.from_)
    smsregex = re.match(r'^<https://voice\.google\.com>[\r\n]+(?P<sms>.*?)[\r\n]+To respond to this text message, ', email.body, re.DOTALL)
    addrregex = re.match(r'^(?P<mynum>\d+?)\.(?P<othernum>\d+?)\.(?P<random>.*?)\@txt.voice.google.com$', email.from_[0][1])
    print(f"""Got new text message!\n
    From: {addrregex.group('othernum')}\n
    {smsregex.group('sms')}""")