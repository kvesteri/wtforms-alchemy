"""
WTForms-Alchemy
---------------

Generates WTForms forms from SQLAlchemy models.
"""

from setuptools import setup, Command
import subprocess
import sys


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call(['py.test'])
        raise SystemExit(errno)


PY3 = sys.version_info[0] == 3


extras_require = {
    'test': [
        'pytest==2.2.3',
        'Pygments>=1.2',
        'Jinja2>=2.3',
        'docutils>=0.10',
        'flexmock>=0.9.7',
        'psycopg2>=2.4.6',
        'WTForms-Test>=0.1.1'
    ],
    'babel': ['Babel>=1.3'],
    'arrow': ['arrow>=0.3.4'],
    'phone': [
        # The phonenumbers library has a split for 2.x and 3.x support.
        'phonenumbers3k==5.6b1' if PY3 else 'phonenumbers<5.6b1'
    ],
    'password': ['passlib >= 1.6, < 2.0'],
    'color': ['colour>=0.0.4'],
    'i18n': ['SQLAlchemy-i18n >= 0.6.3'],
    'ipaddress': ['ipaddr'] if not PY3 else [],
    'timezone': ['python-dateutil']
}


# Add all optional dependencies to testing requirements.
for name, requirements in extras_require.items():
    if name != 'test':
        extras_require['test'] += requirements


setup(
    name='WTForms-Alchemy',
    version='0.8.5',
    url='https://github.com/kvesteri/wtforms-alchemy',
    license='BSD',
    author='Konsta Vesterinen',
    author_email='konsta@fastmonkeys.com',
    description='Generates WTForms forms from SQLAlchemy models.',
    long_description=__doc__,
    packages=['wtforms_alchemy'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'SQLAlchemy>=0.8.0',
        'WTForms>=1.0.4',
        'WTForms-Components>=0.8.0',
        'SQLAlchemy-Utils>=0.19.0',
        'six>=1.4.1',
        'ordereddict>=1.1'
        if sys.version_info[0] == 2 and sys.version_info[1] < 7 else '',
    ],
    extras_require=extras_require,
    cmdclass={'test': PyTest},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
