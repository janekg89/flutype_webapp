# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.db import models
from djchoices import DjangoChoices, ChoiceItem
from django.contrib.auth.models import User
from .helper import OverwriteStorage, CHAR_MAX_LENGTH
from django.apps import apps

class Status(DjangoChoices):
    planning = ChoiceItem("planning")
    in_progress = ChoiceItem("in progress")
    finished = ChoiceItem("finished")


class Statusable(models.Model):
    status = models.CharField(max_length=CHAR_MAX_LENGTH,
                                       choices=Status.choices,
                                       blank=True,
                                       null=True)

    class Meta:
        abstract = True

class Timestampable(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
class Dateable(models.Model):
    date =models.DateField(blank=True, null=True)

class Sidable(models.Model):
    sid = models.CharField(max_length=CHAR_MAX_LENGTH, unique=True)
    class Meta:
        abstract = True

class Userable(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    class Meta:
        abstract = True

class Commentable(models.Model):
    comment = models.TextField(blank=True, null=True)
    class Meta:
        abstract = True


class FileAttachable(models.Model):
    files = models.ManyToManyField("RawDoc",blank=True)

    class Meta:
        abstract = True

class Hidable(models.Model):
    hidden = models.BooleanField(default=False)

    class Meta:
        abstract = True

class Hashable(models.Model):
    hash = models.CharField(max_length=CHAR_MAX_LENGTH,blank=True, null=True)

    class Meta:
        abstract = True


