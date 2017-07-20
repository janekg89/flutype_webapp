# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import RawSpotCollection,SpotCollection
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



class IndexView(generic.ListView):
    template_name = 'flutype/index.html'
    model = RawSpotCollection
    context_object_name = 'RawSpotCollections'

    def get_queryset(self):
        return RawSpotCollection.objects.only('sid')


'''
class RawSpotCollectionView(generic.DetailView):
    model = RawSpotCollection
    template_name = 'flutype/rawspotcollection.html'
'''

def test_view(request, pk):
    rsc = get_object_or_404(RawSpotCollection, id=pk)

    # get spot collections

    context = {
        'rawspotcollection': rsc,
        'html': rsc.pepmap(),
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



