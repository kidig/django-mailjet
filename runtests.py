# python setup.py test
#   or
# python runtests.py

import sys

from django import setup
from django.conf import settings
from django.test.runner import DiscoverRunner as TestRunner


APP = 'django_mailjet'

settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
    },
    ROOT_URLCONF=APP+'.urls',
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        APP,
    ),
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    ),
    TEMPLATES=[
        # Djrill doesn't have any templates, but tests need a TEMPLATES
        # setting to avoid warnings from the Django 1.8+ test client.
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
        },
    ],
)

setup()


def runtests():
    test_runner = TestRunner(verbosity=1)
    failures = test_runner.run_tests([APP])
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
