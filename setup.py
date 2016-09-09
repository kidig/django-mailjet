import re
from os import path
from setuptools import setup


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with open(filename) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


DESCRIPTION = "A Django email backend for Mailjet"

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    pass

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Framework :: Django',
    'Framework :: Django :: 1.9',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    name='django-mailjet',
    version=find_version("django_mailjet", "__init__.py"),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    keywords="django, mailjet, email, email backend",
    author='Dmitrii Gerasimenko',
    author_email='kiddima@gmail.com',
    url='http://github.com/kidig/django-mailjet/',
    license='MIT',
    packages=['django_mailjet'],
    install_requires=[
        "mailjet_rest",
        "django>=1.8",
    ],
    dependency_links=[
        "git+ssh://git@github.com/kidig/mailjet-apiv3-python@bb52d9ed4bc18af3e3a4d5e38643b173e87468ce#egg=mailjet_rest",
    ],
    include_package_data=True,
    tests_require=["mock", "six"],
    test_suite="runtests.runtests",
    zip_safe=False,
)
