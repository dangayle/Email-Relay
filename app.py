import os
import logging

import requests
from flask import Flask, redirect, request, Response

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

CONFIG = {
    "mailgun_domain": os.environ.get("MAILGUN_DOMAIN"),
    "mailgun_api_key": os.environ.get("MAILGUN_API_KEY"),
    "mailgun_public_key": os.environ.get("MAILGUN_PUBLIC_KEY"),
    "mail_to_address": os.environ.get("MAIL_TO_ADDRESS")
}

app = Flask(__name__)


def send_mail(mail_from, mail_to, mail_subject, mail_text):
    """Email relay with ReCaptcha support."""
    try:
        mail_request = requests.post(
            f"https://api.mailgun.net/v3/{CONFIG['mailgun_domain']}/messages",
            auth=("api", f"{CONFIG['mailgun_api_key']}"),
            data={"from": mail_from,
                  "to": [mail_to],
                  "subject": mail_subject,
                  "text": mail_text}
        )
        return mail_request
    except:
        logger.exception("problem with sending mail")



def validate_email(email):
    """Validate email against Mailgun API."""
    try:
        r = requests.get(
            "https://api.mailgun.net/v3/address/validate",
            auth=("api", CONFIG['mailgun_public_key']),
            params={"address": email})
        if r.status_code == requests.codes.ok and r.json()["is_valid"] is True:
            return True
        else:
            return False
    except:
        logger.exception("problem with sending mail")


def validate_form(request):
    """Validate form fields."""
    name = request.form['name']
    email = request.form['email']  # if validate_email(request.form['email']) else False
    text = request.form['text']
    return name, email, text


@app.route('/mail_relay/', methods=['POST'])
def mail_relay():
    """Send an email."""

    name, email, text = validate_form(request)
    if name and email and text:
        mail_from = f"{name} <{email}>"
        mail_subject = f"[contact form] mail from {name}"
        mail_text = text
        mail_to = CONFIG['mail_to_address']
        r = send_mail(mail_from, mail_to, mail_subject, mail_text)
        if r.status_code == requests.codes.ok:
            return r.content, r.status_code
        else:
            return "There was an issue with your request", r.status_code
    else:
        return "There was an issue with your request", 400


@app.route('/')
def hello_world():
    """Hello world."""
    return "Hello world!", 200


if __name__ == '__main__':
    app.run()
