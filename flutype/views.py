# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User

from .forms import PeptideForm
from .models import RawSpotCollection,SpotCollection,Process, PeptideBatch, Peptide, VirusBatch, Virus, AntibodyBatch, Antibody
from django.shortcuts import get_object_or_404, render_to_response,render, redirect

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.views.generic.list import ListView
from django.views.generic.edit import ModelFormMixin


from django.db.models import Max
import json
import plotly.tools as tls
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

def empty_list(max):
    list = []
    for n in range(max):
        list.append('')
    return list

# Create your views here.
@login_required
@api_view(['GET'])
def barplot_data_view(request, pk):
        sc = get_object_or_404(SpotCollection, id=pk)
        all_spots= sc.spot_set.all()
        spot_lig1 = all_spots.values_list("raw_spot__ligand1__sid", flat=True)
        lig1=spot_lig1.distinct()
        box_list=[]
        for lig in lig1:
            a={}
            a["intensity"]=all_spots.filter(raw_spot__ligand1__sid=lig).values_list("intensity", flat=True)
            a["lig2"] = all_spots.filter(raw_spot__ligand1__sid=lig).values_list("raw_spot__ligand2__sid", flat=True)
            a["lig1"] = all_spots.filter(raw_spot__ligand1__sid=lig).values_list("raw_spot__ligand1__ligand__sid").first()
            a["lig1_con"] = all_spots.filter(raw_spot__ligand1__sid=lig).values_list("raw_spot__ligand1__concentration").first()
            box_list.append(a)
        data = {
            "box_list":box_list,
            "lig1":lig1,
            }
        return Response(data)

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
def processes_view(request):
    processes = Process.objects.all()

    context = {
        'processes': processes,
    }
    return render(request,
                  'flutype/processes.html', context)
@login_required
def process_view(request,pk):
    process = get_object_or_404(Process, id=pk)

    context = {
        'process': process,
    }
    return render(request,
                  'flutype/process.html', context)

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

    spots = collection.rawspot_set.all()
    row_max = spots.aggregate(Max('row'))
    column_max = spots.aggregate(Max('column'))
    row_list = empty_list(row_max["row__max"])
    column_list = empty_list(column_max["column__max"])

    data = []
    for spot in spots:
        data.append([spot.column - 1, spot.row - 1, 0])
    context = {
        'lig1': json.dumps(collection.pivot_ligand1().values.tolist()),
        'lig2': json.dumps(collection.pivot_ligand2().values.tolist()),
        'con1': json.dumps(collection.pivot_concentration1().values.tolist()),
        'con2': json.dumps(collection.pivot_concentration2().values.tolist()),
        'type': 'raw',
        'collection': collection,
        'data': json.dumps(data),
        'row_list': json.dumps(row_list),
        'column_list': json.dumps(column_list),
    }
    return render(request,
                  'flutype/spotcollection.html', context)

@login_required
def quantified_spot_collection(request, pk):
    """ Renders detailed SpotCollection View. """

    sc = get_object_or_404(SpotCollection, id=pk)
    collection = sc.raw_spot_collection


    spots = sc.spot_set.all()

    row_max= spots.aggregate(Max('raw_spot__row'))
    column_max= spots.aggregate(Max('raw_spot__column'))

    row_list = empty_list(row_max["raw_spot__row__max"])
    column_list = empty_list(column_max["raw_spot__column__max"])
    data = []
    for spot in spots:
        data.append([spot.raw_spot.column - 1, spot.raw_spot.row - 1, spot.intensity])
##################################################################################

################################
    context = {
        'lig1': json.dumps(sc.raw_spot_collection.pivot_ligand1().values.tolist()),
        'lig2': json.dumps(sc.raw_spot_collection.pivot_ligand2().values.tolist()),
        'con1': json.dumps(sc.raw_spot_collection.pivot_concentration1().values.tolist()),
        'con2': json.dumps(sc.raw_spot_collection.pivot_concentration2().values.tolist()),
        'type': 'quantified',
        'collection': collection,
        'q_collection': sc,
        'data': json.dumps(data),
        'row_list': json.dumps(row_list),
        'column_list': json.dumps(column_list),
    }
    return render(request,
                  'flutype/spotcollection.html', context)


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
    plotly_fig = tls.mpl_to_plotly(fig)
    context = plot(plotly_fig, auto_open=False, output_type='div')

    return context




@login_required
def highcharts_view(request,pk):
    sc = get_object_or_404(SpotCollection, id=pk)
    spots=sc.spot_set.all()
    row_max= spots.aggregate(Max('raw_spot__row'))
    column_max= spots.aggregate(Max('raw_spot__column'))

    row_list = empty_list(row_max["raw_spot__row__max"])
    column_list = empty_list(column_max["raw_spot__column__max"])
    data = []
    for spot in spots:
        data.append([spot.raw_spot.row - 1, spot.raw_spot.column - 1, spot.intensity])
    context = {
        'lig1': json.dumps(sc.raw_spot_collection.pivot_ligand1().values.tolist()),
        'lig2': json.dumps(sc.raw_spot_collection.pivot_ligand2().values.tolist()),
        'con1': json.dumps(sc.raw_spot_collection.pivot_concentration1().values.tolist()),
        'con2': json.dumps(sc.raw_spot_collection.pivot_concentration2().values.tolist()),
        'data': json.dumps(data),
        'row_list':json.dumps(row_list),
        'column_list':json.dumps(column_list),
    }
    return render(request,
                  'flutype/highcharts.html', context)



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

@login_required
def peptide_new(request):
    if request.method == 'POST':
        form = PeptideForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('peptides')
    else:
        form = PeptideForm()
        return render(request,'flutype/create_peptide.html',{'form':form})

