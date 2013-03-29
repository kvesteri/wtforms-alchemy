"""
WTForms-Alchemy
---------------

Generates WTForms forms from SQLAlchemy models.
"""

from setuptools import setup, Command
import subprocess


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call(['py.test'])
        raise SystemExit(errno)

setup(
    name='WTForms-Alchemy',
    version='0.4.5',
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
        'SQLAlchemy>=0.7.8',
        'WTForms>=1.0.2',
        'WTForms-Components>=0.4.6',
        'SQLAlchemy-Utils>=0.7.7'
    ],
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
