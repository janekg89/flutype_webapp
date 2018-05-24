"""
Setup of django environment.

Import this module to perform the setup

    from flutype.utils import django_setup
"""
import os
import sys

FILE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)))
PROJECT_DIR = os.path.join(FILE_DIR, "../../")
sys.path.append(PROJECT_DIR)

# This is so Django knows where to find stuff.
os.environ.setdefault('DJANGO_SETTINGS_MODULE','flutype_webapp.settings')

# django setup
import django
django.setup()
