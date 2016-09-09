
import mimetypes
from base64 import b64encode
from email.mime.base import MIMEBase
from email.utils import parseaddr
from mailjet_rest import Client


from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address, DEFAULT_ATTACHMENT_MIME_TYPE

from .exceptions import MailjetError, MailjetAPIError


class MailjetBackend(BaseEmailBackend):
    """
    Mailjet email backend for Django
    """

    def __init__(self, fail_silently=False, *args, **kwargs):
        super(MailjetBackend, self).__init__(fail_silently=fail_silently, *args, **kwargs)

        try:
            self._api_key = settings.MAILJET_API_KEY
            self._api_secret = settings.MAILJET_API_SECRET
        except AttributeError:
            if not fail_silently:
                raise ImproperlyConfigured("Please set MAILJET_API_KEY and MAILJET_API_SECRET in settings.py to use Mailjet")

        self.client = Client(auth=(self._api_key, self._api_secret))

    def open(self):
        pass

    def close(self):
        pass

    def _parse_recipients(self, message, recipients):
        rcpts = []
        recipient_vars = getattr(message, 'recipient_vars', {})

        for addr in recipients:
            to_name, to_email = parseaddr(sanitize_address(addr, message.encoding))
            rcpt = {'Email': to_email, 'Name': to_name}

            if recipient_vars.get(addr):
                rcpt['Vars'] = recipient_vars.get(addr)

            rcpts.append(rcpt)
        return rcpts

    def _send(self, message):
        message.mailjet_response = None
        if not message.recipients():
            return False


        try:
            payload = self.build_send_payload(message)
            response = self.post_to_mailjet(payload, message)

            message.mailjet_response = self.parse_response(response, payload, message)

        except MailjetError:
            if not self.fail_silently:
                raise
            return False

        return True

    def build_send_payload(self, message):
        msg_dict = self._build_standart_message_dict(message)
        self._add_mailjet_options(message, msg_dict)

        if getattr(message, 'alternatives', None):
            self._add_alternatives(message, msg_dict)

        self._add_attachments(message, msg_dict)

        return msg_dict

    def post_to_mailjet(self, payload, message):
        response = self.client.send.create(data=payload)
        if response.status_code != 200:
            raise MailjetAPIError(email_message=message, payload=payload, response=response)
        return response

    def parse_response(self, response, payload, message):
        try:
            return response.json()
        except ValueError:
            raise MailjetAPIError("Invalid JSON in Mailjet API response",
                email_message=message, payload=payload, response=response)

    def _build_standart_message_dict(self, message):
        msg_dict = dict()

        if len(message.subject):
            msg_dict['Subject'] = message.subject

        if len(message.body):
            msg_dict['Text-part'] = message.body

        sender = sanitize_address(message.from_email, message.encoding)
        from_name, from_email = parseaddr(sender)

        msg_dict['FromEmail'] = from_email
        msg_dict['FromName'] = from_name

        # msg_dict['To'] = message.to
        msg_dict['Recipients'] = self._parse_recipients(message, message.to)

        if hasattr(message, 'cc'):
            msg_dict['Cc'] = message.cc

        if hasattr(message, 'bcc'):
            msg_dict['bcc'] = message.bcc

        if hasattr(message, 'reply_to'):
            reply_to = [sanitize_address(addr, message.encoding) for addr in message.reply_to]
            msg_dict['Headers'] = {'Reply-To': ', '.join(reply_to)}

        if message.extra_headers:
            msg_dict['Headers'] = msg_dict.get('Headers', {})
            msg_dict['Headers'].update(message.extra_headers)

        return msg_dict

    def _add_mailjet_options(self, message, msg_dict):
        mailjet_attrs = {
            'template_id': 'Mj-TemplateID',
            'template_language': 'Mj-TemplateLanguage',
            'template_error_reporting': 'Mj-TemplateErrorReporting',
            'template_error_deliver': 'Mj-TemplateErrorDeliver',
            'campaign': 'Mj-Campaign',
            'deduplicate_campaign': 'Mj-deduplicatecampaign',
            'track_open': 'Mj-trackopen',
            'track_click': 'Mj-trackclick',
            'custom_id': 'Mj-CustomID',
            'event_payload': 'Mj-EventPayLoad',
        }

        for attr, mj_attr in mailjet_attrs.items():
            if hasattr(message, attr):
                msg_dict[mj_attr] = getattr(message, attr)

        if hasattr(message, 'template_vars'):
            msg_dict['Vars'] = message.template_vars

    def _add_alternatives(self, message, msg_dict):
        for alt in message.alternatives:
            content, mimetype = alt
            if mimetype == 'text/html':
                msg_dict['Html-part'] = content
                break

    def _add_attachments(self, message, msg_dict):
        if not message.attachments:
            return

        str_encoding = message.encoding or settings.DEFAULT_CHARSET
        mj_attachments = []
        mj_inline_attachments = []
        for attachment in message.attachments:
            att_dict, is_inline = self._make_attachment(attachment, str_encoding)
            if is_inline:
                mj_inline_attachments.append(att_dict)
            else:
                mj_attachments.append(att_dict)

        if mj_attachments:
            msg_dict['Attachments'] = mj_attachments
        if mj_inline_attachments:
            msg_dict['Inline_attachments'] = mj_inline_attachments

    def _make_attachment(self, attachment, str_encoding=None):
        """Returns EmailMessage.attachments item formatted for sending with Mailjet

        Returns mailjet_dict, is_inline_image
        """
        is_inline_image = False
        if isinstance(attachment, MIMEBase):
            name = attachment.get_filename()
            content = attachment.get_payload(decode=True)
            mimetype = attachment.get_content_type()

            if attachment.get_content_maintype() == 'image' and attachment['Content-ID'] is not None:
                is_inline_image = True
                name = attachment['Content-ID']
        else:
            (name, content, mimetype) = attachment

        # Guess missing mimetype from filename, borrowed from
        # django.core.mail.EmailMessage._create_attachment()
        if mimetype is None and name is not None:
            mimetype, _ = mimetypes.guess_type(name)
        if mimetype is None:
            mimetype = DEFAULT_ATTACHMENT_MIME_TYPE

        try:
            # noinspection PyUnresolvedReferences
            if isinstance(content, unicode):
                # Python 2.x unicode string
                content = content.encode(str_encoding)
        except NameError:
            # Python 3 doesn't differentiate between strings and unicode
            # Convert python3 unicode str to bytes attachment:
            if isinstance(content, str):
                content = content.encode(str_encoding)

        content_b64 = b64encode(content)

        mj_attachment = {
            'Content-type': mimetype,
            'Filename': name or '',
            'content': content_b64.decode('ascii'),
        }
        return mj_attachment, is_inline_image

    def send_messages(self, email_messages):
        if not email_messages:
            return

        num_sent = 0
        for message in email_messages:
            if self._send(message):
                num_sent += 1

        return num_sent
