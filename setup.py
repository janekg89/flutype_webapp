import os
import re
import io

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'flutype_webapp.settings'
import django
django.setup()

setup_kwargs = {}
# read the version and info file
def read(*names, **kwargs):
    """ Read file info in correct encoding. """
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()

try:
    verstrline = read('flutype/_version.py')
    mo = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", verstrline, re.M)
    if mo:
        verstr = mo.group(1)
        setup_kwargs['version'] = verstr
    else:
        raise RuntimeError("Unable to find version string")
except Exception as e:
    print('Could not read version: {}'.format(e))

setup(
    name='flutype_db',
    packages=find_packages(),
    include_package_data=True,
    license='LGPLv3',
    description='A web-database for virus-peptide interactions',
    long_description=README,
    url='https://www.flutype.de/',
    author='Jan Grzegorzewski & Matthias König',
    author_email='janekg89@hotmail.de',
    **setup_kwargs
)