# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import RawSpotCollection,SpotCollection, PeptideBatch
from django.views import generic
from django.shortcuts import render, get_object_or_404

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

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




def index_view(request):
    collections = RawSpotCollection.objects.all()
    context = {
        'collections': collections,
    }
    return render(request,
                  'flutype/index.html', context)

def peptide_batch_view(request):
    peptide_batches = PeptideBatch.objects.all()
    context = {
        'peptide_batches': peptide_batches,
    }
    return render(request,
                  'flutype/peptidebatch.html', context)


# FIXME: naming of function
def raw_spot_collection_detail_view(request, pk):
    """ Renders detailed RawSpotCollection View.

    :param request:
    :param pk:
    :return:
    """
    rsc = get_object_or_404(RawSpotCollection, id=pk)

    # get spot collections

    context = {
        'type': 'rawspotcollection',
        'rawspotcollection': rsc,
    }
    return render(request,
                  'flutype/rawspotcollection.html', context)



def heatmap_view(request, pk):
    """ View to render a heatmap as png response.

    :param request:
    :param pk:
    :return:
    """
    rsc = get_object_or_404(RawSpotCollection, id=pk)

    # create a matplotlib plot
    ana = rsc.analysis()

    # ! the figure must be created with:
    # from matplotlib.figure import Figure
    # fig = Figure(**kwargs)
    fig = ana.heatmap(heatmap=False, figsize=(20, 10))

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response




class SpotCollectionView(generic.DetailView):
    model = SpotCollection
    template_name = 'flutype/spotcollection.html'

"""
class PepMap(generic.DetailView):
    model = SpotCollection
    return HttpResponse(RawSpotCollection.pepmap())
"""



