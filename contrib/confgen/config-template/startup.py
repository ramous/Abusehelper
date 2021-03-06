import os
from abusehelper.core.config import relative_path

class Bot(object):
    # The default credentials used for XMPP connections.
    xmpp_jid = "@XMPP_JID@"
    xmpp_password = "@XMPP_PASSWORD@"

    # The XMPP multi-user chat room used for bot control.
    service_room = "@SERVICE_ROOM@"

    def __init__(self, name, **attrs):
        self.attrs = dict(
            module="abusehelper.core."+name,
            bot_name=name,

            # Unomment the following lines, and the bots will keep
            # persistent state and log to files, respectively.
            #bot_state_file=relative_path("state", name + ".state"),
            #log_file=relative_path("log", name + ".log"),

            xmpp_jid=self.xmpp_jid,
            xmpp_password=self.xmpp_password,
            service_room=self.service_room,
            )
        self.attrs.update(attrs)

    def startup(self):
        return self.attrs

def configs():
    # Launch a fine selection of abusehelper.core.* bots
    yield Bot("mailer",
              smtp_host="@SMTP_HOST@",
              smtp_port="@SMTP_PORT@",
              smtp_auth_user="@SMTP_AUTH_USER@",
              smtp_auth_password="@SMTP_AUTH_PASSWORD@",
              mail_sender="@MAIL_SENDER@")
    yield Bot("wikibot")
    yield Bot("dshield")
    yield Bot("roomgraph")
    yield Bot("historian")
    yield Bot("runtime", config=relative_path("runtime.py"))

    # Find and launch modules named custom/*.sanitizer.py
    for filename in os.listdir(relative_path("custom")):
        if filename.endswith(".sanitizer.py"):
            yield Bot(name=filename[:-3], 
                      module=relative_path("custom", filename))
