#!/usr/bin/python -tt

setupArgs = {
    'name': 'zuora',
    'version': '1.0.21',
    'author': 'MapMyFitness (Guidebook fork)',
    'author_email': 'naoya@guidebook.com',
    'url': 'http://github.com/naoyak/python-zuora',
    'description': 'Zuora client library.',
    'packages': [
        'zuora',
        'zuora.rest_wrapper',
    ],
}

try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup
else:
    import sys
    import subprocess

    class TestRunner(Command):
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            errno = subprocess.call(['py.test'])
            sys.exit(errno)

    setupArgs.update({
        'tests_require': ['pytest'],
        'cmdclass': {'test': TestRunner},
        'install_requires': ['suds-jurko >= 0.6', 'requests', 'httplib2'],
        'zip_safe': False,
    })

setup(**setupArgs)
