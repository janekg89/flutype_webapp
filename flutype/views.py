# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import RawSpotCollection,SpotCollection, PeptideBatch, Peptide, VirusBatch, Virus
from django.views import generic
from django.shortcuts import render, get_object_or_404

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


# TODO: filter functions to display subset (from

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
                  'flutype/peptidebatches.html', context)

def peptide_view(request):
    peptides = Peptide.objects.all()
    context = {
        'peptides': peptides,
    }
    return render(request,
                  'flutype/peptides.html', context)
def virus_batch_view(request):
    virus_batches = VirusBatch.objects.all()
    context = {
        'virus_batches': virus_batches,
    }
    return render(request,
                  'flutype/virusbatches.html', context)

def virus_view(request):
    viruses = Virus.objects.all()
    context = {
        'viruses': viruses,
    }
    return render(request,
                  'flutype/viruses.html', context)


def raw_spot_collection(request, pk):
    """ Renders detailed RawSpotCollection View. """

    collection = get_object_or_404(RawSpotCollection, id=pk)
    context = {
        'type': 'raw',
        'collection': collection,
    }
    return render(request,
                  'flutype/spotcollection.html', context)


def quantified_spot_collection(request, pk):
    """ Renders detailed SpotCollection View. """

    q_collection = get_object_or_404(SpotCollection, id=pk)
    collection = q_collection.raw_spot_collection

    context = {
        'type': 'quantified',
        'collection': collection,
        'q_collection': q_collection,
    }
    return render(request,
                  'flutype/spotcollection.html', context)


def raw_spot_collection_detail_view(request, pk):
    """ Renders detailed RawSpotCollection View. """

    rsc = get_object_or_404(RawSpotCollection, id=pk)
    context = {
        'type': 'rawspotcollection',
        'rawspotcollection': rsc,
    }
    return render(request,
                  'flutype/spotcollection.html', context)


class SpotCollectionView(generic.DetailView):
    model = SpotCollection
    template_name = 'flutype/spotcollection.html'



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
