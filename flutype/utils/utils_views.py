# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.shortcuts import redirect


def delete_posted_and_redirect(instance):
    instance.delete()
    return redirect(instance.__class__.url())

def save_posted_and_redirect(instance):
    instance.save()
    return redirect(instance.__class__.url())