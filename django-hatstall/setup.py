import codecs
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
readme_md = os.path.join(here, 'README.rst')

with codecs.open(readme_md, encoding='utf-8') as f:
    long_description = f.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-hatstall',
    version='0.1.2',
    packages=['hatstall'],
    include_package_data=True,
    license='GPLv3',
    description='A Django app to manage identities in Sorting Hat.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/chaoss/grimoirelab-hatstall',
    author='Bitergia',
    author_email='acs@bitergia.com',
    keywords="development repositories analytics git github bugzilla jira jenkins",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Customer Service',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'django>=2.0',
    ]
)
