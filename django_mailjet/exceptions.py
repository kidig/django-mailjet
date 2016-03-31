import json
from requests import HTTPError


class MailjetError(Exception):

    def __init__(self, *args, **kwargs):
        self.email_message = kwargs.pop('email_message', None)
        self.payload = kwargs.pop('payload', None)

        if isinstance(self, HTTPError):
            self.response = kwargs.get('response', None)
        else:
            self.response = kwargs.pop('response', None)

        super(MailjetError, self).__init__(*args, **kwargs)

    def __str__(self):
        parts = [
            " ".join([str(arg) for arg in self.args]),
            self.describe_send(),
            self.describe_response(),
        ]
        return "\n".join(filter(None, parts))

    def describe_send(self):
        if self.payload is None:
            return None
        description = "Sending a message"
        try:
            to_emails = [to['email'] for to in self.payload['message']['to']]
            description += " to %s" % ','.join(to_emails)
        except KeyError:
            pass
        try:
            description += " from %s" % self.payload['message']['from_email']
        except KeyError:
            pass
        return description

    def describe_response(self):
        if self.response is None:
            return None
        description = "Mailjet API response %d: %s" % (self.response.status_code, self.response.reason)

        try:
            json_response = self.response.json()
            description += "\n" + json.dumps(json_response, indent=2)
        except (AttributeError, KeyError, ValueError):
            try:
                description += " " + self.response.text
            except AttributeError:
                pass
        return description


class MailjetAPIError(MailjetError, HTTPError):

    def __init__(self, *args, **kwargs):
        super(MailjetAPIError, self).__init__(*args, **kwargs)
        if self.response is not None:
            self.status_code = self.response.status_code
