# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import RawSpotCollection,Process
from django.views import generic
"""
def index(request):
    return HttpResponse("What do you want to do?")

#def peptide(request):
#    return HttpResponse("See peptide list")


def peptide_batch(request):
    return HttpResponse("See peptidebatch list")

#def virus(request):
#    return HttpResponse("See virus list")

def virus_batch(request):
    return HttpResponse("See virusbatch list")

def process_list(request):
    return HttpResponse("See process list")
"""





class IndexView(generic.ListView):
    template_name = 'flutype/index.html'
    model = RawSpotCollection
    context_object_name = 'RawSpotCollection'

    def get_queryset(self):
        return RawSpotCollection.objects.only('sid')


class DetailView(generic.DetailView):
    model = RawSpotCollection
    template_name = 'flutype/detail.html'



