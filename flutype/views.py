# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import RawSpotCollection,SpotCollection, PeptideBatch, Peptide, VirusBatch, Virus, AntibodyBatch, Antibody
from django.views import generic
from django.shortcuts import render, get_object_or_404

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect

# @login_required
def test_view(request):
    context = {
        'data': 123,
        'user': 'testuser'
    }
    return render(request,
                  'flutype/test.html', context)


@login_required
def index_view(request):
    collections = RawSpotCollection.objects.all()

    context = {
        'type': 'all',
        'collections': collections,
    }
    return render(request,
                  'flutype/index.html', context)
@login_required
def my_index_view(request):

    collections = RawSpotCollection.objects.filter(process__processstep__user=request.user).distinct()

    print(collections.values_list("sid", flat=True))
    context = {
        'type': 'my',
        'collections': collections,
    }
    return render(request,
                  'flutype/index.html', context)

@login_required
def users_view(request):
    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request,
                  'flutype/users.html', context)

def about_view(request):
    return render(request,"flutype/about.html")


@login_required
def peptide_batch_view(request):
    peptide_batches = PeptideBatch.objects.all()
    context = {
        'peptide_batches': peptide_batches,
    }
    return render(request,
                  'flutype/peptidebatches.html', context)

@login_required
def peptide_batch_mobile_view(request):
    peptide_batches = PeptideBatch.objects.filter(ligand2__isnull=False).distinct()
    context = {
        'type': "mobile",
        'peptide_batches': peptide_batches,
    }
    return render(request,
                  'flutype/peptidebatches.html', context)
@login_required
def peptide_batch_fixed_view(request):
    peptide_batches = PeptideBatch.objects.filter(ligand1__isnull=False).distinct()
    context = {
        'type': "fixed",
        'peptide_batches': peptide_batches,
    }
    return render(request,
                  'flutype/peptidebatches.html', context)



@login_required
def peptide_view(request):
    peptides = Peptide.objects.all()
    context = {
        'peptides': peptides,
    }
    return render(request,
                  'flutype/peptides.html', context)
@login_required
def peptide_mobile_view(request):
    peptides = Peptide.objects.filter(ligands2__isnull=False).distinct()
    context = {
        'type': "mobile",
        'peptides': peptides,
    }
    return render(request,
                  'flutype/peptides.html', context)
@login_required
def peptide_fixed_view(request):
    peptides = Peptide.objects.filter(ligands1__isnull=False).distinct()

    context = {
        'type': "fixed",
        'peptides': peptides,
    }
    return render(request,
                  'flutype/peptides.html', context)


@login_required
def virus_batch_view(request):
    virus_batches = VirusBatch.objects.all()
    context = {
        'virus_batches': virus_batches,
    }
    return render(request,
                  'flutype/virusbatches.html', context)


@login_required
def virus_batch_mobile_view(request):
    virus_batches = VirusBatch.objects.filter(ligand2__isnull=False).distinct()
    context = {

        'type': "mobile",
        'virus_batches': virus_batches,
    }
    return render(request,
                  'flutype/virusbatches.html', context)

@login_required
def virus_batch_fixed_view(request):
    virus_batches = VirusBatch.objects.filter(ligand1__isnull=False).distinct()
    context = {
        'type': "fixed",
        'virus_batches': virus_batches,
    }
    return render(request,
                  'flutype/virusbatches.html', context)

@login_required
def antibody_batch_view(request):
    antibody_batches = AntibodyBatch.objects.all()
    context = {
        'antibody_batches': antibody_batches,
    }
    return render(request,
                  'flutype/antibodybatches.html', context)


@login_required
def antibody_batch_mobile_view(request):
    antibody_batches = AntibodyBatch.objects.filter(ligand2__isnull=False).distinct()
    context = {
        'type': "mobile",

        'antibody_batches': antibody_batches,
    }
    return render(request,
                  'flutype/antibodybatches.html', context)

@login_required
def antibody_batch_fixed_view(request):
    antibody_batches = AntibodyBatch.objects.filter(ligand1__isnull=False).distinct()
    context = {
        'type': "fixed",
        'antibody_batches': antibody_batches,
    }
    return render(request,
                  'flutype/antibodybatches.html', context)
@login_required
def antibody_view(request):
    antibodies = Antibody.objects.all()
    context = {
        'antibodies': antibodies,
    }
    return render(request,
                  'flutype/antibodies.html', context)


@login_required
def antibody_mobile_view(request):
    antibodies = Antibody.objects.filter(ligands2__isnull=False).distinct()
    context = {
        'type': "mobile",
        'antibodies': antibodies,
    }
    return render(request,
                  'flutype/antibodies.html', context)


@login_required
def antibody_fixed_view(request):
    antibodies = Antibody.objects.filter(ligands1__isnull=False).distinct()
    context = {
        'type': "fixed",

        'antibodies': antibodies,
    }
    return render(request,
                  'flutype/antibodies.html', context)


@login_required
def virus_view(request):
    viruses = Virus.objects.all()
    context = {

        'viruses': viruses,
    }
    return render(request,
                  'flutype/viruses.html', context)
@login_required
def virus_mobile_view(request):
    viruses = Virus.objects.filter(ligands2__isnull=False).distinct()
    context = {
        'type': "mobile",
        'viruses': viruses,
    }
    return render(request,
                  'flutype/viruses.html', context)
@login_required
def virus_fixed_view(request):
    viruses = Virus.objects.filter(ligands1__isnull=False).distinct()

    context = {
        'type': "fixed",
        'viruses': viruses,
    }
    return render(request,
                  'flutype/viruses.html', context)

@login_required
def raw_spot_collection(request, pk):
    """ Renders detailed RawSpotCollection View. """

    collection = get_object_or_404(RawSpotCollection, id=pk)
    context = {
        'type': 'raw',
        'collection': collection,
    }
    return render(request,
                  'flutype/spotcollection.html', context)

@login_required
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

@login_required
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

@login_required
def heatmap_view(request, pk):
    """ View to render a heatmap as png response.

    :param request:
    :param pk:
    :return:
    """

    sc = get_object_or_404(SpotCollection, id=pk)

    # create a matplotlib plot
    ana = sc.analysis()

    # ! the figure must be created with:
    # from matplotlib.figure import Figure
    # fig = Figure(**kwargs)

    fig = ana.heatmap(heatmap=True, descript=False, figsize=(10, 15))

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response

# FIXME: typo
@login_required
def desciptmap_view(request, pk):
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

    fig = ana.heatmap(heatmap=False, descript=True, figsize=(10, 15))

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response

@login_required
def barplot_view(request, pk):
    """ View to render a heatmap as png response.

    :param request:
    :param pk:
    :return:
    """

    sc = get_object_or_404(SpotCollection, id=pk)

    # create a matplotlib plot
    ana = sc.analysis()

    # ! the figure must be created with:
    # from matplotlib.figure import Figure
    # fig = Figure(**kwargs)


    fig = ana.barplot(align="vir", scale="log", figsize=(20, 10))

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
        })