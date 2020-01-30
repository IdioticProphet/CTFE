from flask import current_app
from app import mail
from flask_mail import Message
from threading import Thread


def send_async_email(flask_app, msg):
    with flask_app.app_context():
        mail.send(msg)
        
class Emailer:
    def __init__(self, subject="Blank Subject", sender="", recipients=["noone"], body=""):
        app = current_app._get_current_object()
        self.msg = Message(subject, sender=app.config.get("MAIL_USERNAME"), recipients=recipients)
        self.msg.body = body
        thr = Thread(target=send_async_email, args=[app, self.msg])
        thr.start()
