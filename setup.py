import os

from setuptools import find_packages
from setuptools import setup

version = '1.0'

install_requires = [
]

tests_require = install_requires + ['Sphinx', 'docutils',
                                    'virtualenv', 'nose', 'coverage']

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.md')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.md')).read()
except IOError:
    README = CHANGES = ''

kwargs = dict(
    version=version,
    name='strava',
    description='Python wrapper for the Strava (http://www.strava.com) API',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
      'Intended Audience :: Developers',
      'Programming Language :: Python',
      'License :: OSI Approved :: Apache Software License',
    ],
    install_requires=install_requires,
    license='Apache',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    tests_require=tests_require,
    test_suite='strava.tests',
    url='https://github.com/Packetslave/strava',
    author='Brian Landers',
    author_email='brian@610systems.com',
    entry_points="""\
    """
)

setup(**kwargs)
