import os
import unittest

import flask
import requests

from app import send_mail, hello_world, app, validate_form


CONFIG = {
    "test_mail_to_address": os.environ.get("TEST_MAIL_TO_ADDRESS"),
    "test_mail_from_address": os.environ.get("TEST_MAIL_FROM_ADDRESS")
}


class testEmailRelay(unittest.TestCase):

    def setUp(self):
        self.test_client = app.test_client()
        self.mail_from_name = "Test app"
        self.mail_from = CONFIG['test_mail_from_address']
        self.mail_to = CONFIG['test_mail_to_address']
        self.mail_subject = "[contact form] test email"
        self.mail_text = "This is a test email. Please ignore."

    def tearDown(self):
        pass

    def test_send_mail(self):
        # TODO: Mock the real Mailgun response
        r = send_mail(self.mail_from, self.mail_to,
                      self.mail_subject, self.mail_text)
        self.assertEqual(r.status_code, requests.codes.ok)
        self.assertEqual(r.json()["message"], "Queued. Thank you.")


    def test_mail_relay(self):

        # TODO: Mock the real Mailgun response
        r = self.test_client.post(
            '/mail_relay/',
            data={
                'name': self.mail_from_name,
                'email': self.mail_from,
                'text': self.mail_text
            }
        )

        self.assertEqual(r.status_code, requests.codes.ok)


    def test_validate_form(self):

        with app.test_request_context(
            '/mail_relay/',
            method='POST',
            data={
                'name': self.mail_from_name,
                'email': self.mail_from,
                'text': self.mail_text
        }):
            assert flask.request.path == '/mail_relay/'
            r = validate_form(flask.request)
            self.assertEqual(r, (self.mail_from_name, self.mail_from,
                                 self.mail_text))

    def test_validate_form(self):
        self.assertEqual(1, 2)

    def test_reCaptcha(self):
        self.assertEqual(1, 2)

    def test_hello_world(self):
        hello = hello_world()
        self.assertEqual(hello, ("Hello world!", 200))
