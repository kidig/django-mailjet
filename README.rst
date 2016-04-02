==============
Django-Mailjet
==============
A Django email backend for use with Mailjet - https://www.mailjet.com/

Overview
========
Django-Mailjet is a drop-in mail backend for Django.

Getting going
=============
Install django-mailjet::
    pip install django-mailjet
Add the following to your ``settings.py``::

    EMAIL_BACKEND = 'django_mailjet.backends.MailjetBackend'
    MAILJET_API_KEY = 'API-KEY'
    MAILJET_API_SECRET = 'API-SECRET'

Replace ``API-KEY`` and ``API-SECRET`` with the values from your Mailjet account details.

Now, when you use ``django.core.mail.send_mail``, Mailjet will send the messages.

.. _Mailjet: http://mailjet.com

*NOTE*: Django-Mailjet does **NOT**
validate your data for compliance with Mailjet's API.
You must ensure what you send is appropriate.


Django Email Backend Reference
================================
* https://docs.djangoproject.com/en/dev/topics/email/#email-backends
