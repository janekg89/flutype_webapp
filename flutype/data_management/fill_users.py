# -*- coding: utf-8 -*-
"""
Create users in the database.
"""
from __future__ import print_function, absolute_import, division
import os
import sys

# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))

if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django

django.setup()
from django.contrib.auth.models import User
from flutype_webapp.settings import DEFAULT_USER_PASSWORD

from collections import namedtuple

########################################################
UserDef = namedtuple('UserDef', ['username', 'first_name', 'last_name', 'email'])
user_defs = [
    UserDef("hmemczak", "Henry", "Memczak", "memczak@uni-potsdam.de"),
    UserDef("mhovestaedt", "Marc", "Hovestädt", "hovestaedt@uni-potsdam.de"),
    UserDef("ssaenger", "Sandra", "Sänger", "SaengerS@rki.de"),
    UserDef("bay", "Bernhard", "Ay", "aybernha@uni-potsdam.de"),
    UserDef("thofmeister", "Theresa", "Hofmeister", "theresa.hofmeister@uni-potsdam.de"),
    UserDef("pbecker", "Paul", "Becker", "pc-becker@gmx.de"),
    UserDef("fbier", "Frank", "Bier", "Frank.Bier@izi-bb.fraunhofer.de"),
    UserDef("herzigk", "Katjana", "Herzig",None),
]
superuser_defs = [
    UserDef("janekg89", "Jan", "Grzegorzewski", "janekg89@hotmail.de"),
    UserDef("mkoenig", "Matthias", "König", "konigmatt@googlemail.com"),
]
########################################################


def create_users(user_defs, delete_all=True):
    """ Create users in database from user definitions.

    :param delete_all: deletes all existing users
    :return:
    """
    if user_defs is None:
        user_defs = []

    # deletes all users
    if delete_all:
        User.objects.all().delete()

    # adds user to database
    for user_def in user_defs:
        # special pattern for user creation required
        user = User.objects.create_user(username=user_def.username, email=user_def.email,
                                        password=DEFAULT_USER_PASSWORD)
        user.last_name = user_def.last_name
        user.first_name = user_def.first_name
        user.save()
    for superuser_def in superuser_defs:
        user = User.objects.create_superuser(username=superuser_def.username,email=superuser_def.email,password=DEFAULT_USER_PASSWORD)
        user.last_name = superuser_def.last_name
        user.first_name = superuser_def.first_name

    for user in User.objects.all():
        print('\t', user.username, user.email, user.password)



if __name__ == "__main__":
    print("*** Creating users ***")
    create_users(user_defs=user_defs, delete_all=True)
