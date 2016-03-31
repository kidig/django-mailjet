from __future__ import unicode_literals

import os
import unittest

from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings

from django_mailjet import MailjetError, MailjetAPIError


MAILJET_TEST_API_KEY = os.getenv('MAILJET_TEST_API_KEY')
MAILJET_TEST_API_SECRET = os.getenv('MAILJET_TEST_API_SECRET')


@unittest.skipUnless(MAILJET_TEST_API_KEY,
            "Set MAILJET_TEST_API_KEY environment variable to run integration tests")
@unittest.skipUnless(MAILJET_TEST_API_SECRET,
            "Set MAILJET_TEST_API_SECRET environment variable to run integration tests")
@override_settings(MAILJET_API_KEY=MAILJET_TEST_API_KEY,
                   MAILJET_API_SECRET=MAILJET_TEST_API_SECRET,
                   EMAIL_BACKEND="django_mailjet.backends.MailjetBackend")
class DjrillIntegrationTests(TestCase):
    """Mailjet API integration tests

    These tests run against the **live** Mailjet API, using the
    environment variable `MAILJET_TEST_API_KEY` as the API key
    and `MAILJET_TEST_API_SECRET` as the API secret.
    If that variable is not set, these tests won't run.

    """

    def setUp(self):
        self.message = mail.EmailMultiAlternatives(
            'Subject', 'Text content', 'from@example.com', ['to@example.com'])
        self.message.attach_alternative('<p>HTML content</p>', "text/html")

    def test_send_mail(self):
        # Example of getting the Mailjet send status
        self.assertEqual(sent_count, 1)
        # noinspection PyUnresolvedReferences
        response = self.message.mailjet_response

        self.assertEqual(response.keys(), {'Sent'})
        self.assertEqual(response['Sent'][0].keys(), {'Email', 'MessageID'})
        self.assertEqual(response['Sent'][0]['Email'], 'to@example.com')
        self.assertGreater(len(response['Sent']), 0)

    @override_settings(MAILJET_API_KEY="Hey, that's not an API key!")
    def test_invalid_api_key(self):
        # Example of trying to send with an invalid MAILJET_API_KEY
        try:
            self.message.send()
            self.fail("This line will not be reached, because send() raised an exception")
        except MailjetAPIError as err:
            self.assertEqual(err.status_code, 401)
            self.assertIn("Unauthorized", str(err))
