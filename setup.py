from setuptools import setup

version = '0.2.0'

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
    version=version,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    keywords="django, mailjet, email, email backend",
    author='Dmitrii Gerasimenko',
    author_email='kiddima@gmail.com',
    url='http://github.com/kidig/django-mailjet/',
    license='MIT',
    packages=['django_mailjet'],
    install_requires=["mailjet_rest>=v1.1.1", "django>=1.8"],
    include_package_data=True,
    tests_require=["mock", "six"],
    test_suite="runtests.runtests",
    zip_safe=False,
)
