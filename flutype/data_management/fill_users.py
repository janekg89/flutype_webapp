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
#deletes all users
User.objects.all().delete()
#defines all users

# FIXME: The usernames CANNOT BE HARDCODED in git !!! SECURITY BREACH.
janek = {"username":"janekg89",
         "first_name":"Jan",
         "last_name":"Grzegorzewski",
         "password":"flutype_db",
         "email":"janekg89@hotmail.de"}

marc = {"username":"Marc.H",
        "first_name":"Marc",
        "last_name":"Hovestaedt",
        "password":"flutype_db",
        "email":"marc.hovestaedt@uni-potsdam.de"}

henry = {"username":"Henry.M",
        "first_name":"Henry",
        "last_name":"Memczak",
        "password":"flutype_db",
        "email":"memczak@uni-potsdam.de"}

sandra = {"username":"Sandra.S",
        "first_name":"Sandra",
        "last_name":"Saenger",
        "password":"flutype_db",
        "email":"SaengerS@rki.de"}

bernhard = {"username":"Bernhard.A",
        "first_name":"Bernhard",
        "last_name":"Ay",
        "password":"flutype_db",
        "email":"aybernha@uni-potsdam.de"}

matthias ={"username":"Matthias.K",
        "first_name":"Matthias",
        "last_name":"Koenig",
        "password":"flutype_db",
        "email":"konigmatt@googlemail.com"}

users = [janek, marc, henry, sandra, bernhard, matthias]

# adds user to database
for user in users:
    user_db = User.objects.create_user(username=user["username"],email=user["email"], password=user["password"])
    user_db.last_name = user["last_name"]
    user_db.first_name = user["first_name"]
    user_db.save()

