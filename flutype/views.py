# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User

from .helper import generate_tree, tar_tree, empty_list
from .forms import PeptideForm, VirusForm, AntibodyForm, AntibodyBatchForm, \
    PeptideBatchForm, VirusBatchForm, ProcessStepForm, ComplexBatchForm, ComplexForm, StudyForm, MeasurementForm, \
    WashingForm,DryingForm,SpottingForm, QuenchingForm,BlockingForm,IncubatingForm, \
    ScanningForm, IncubatingAnalytForm, RawDocForm
from .models import RawSpotCollection, SpotCollection, Process, PeptideBatch, \
    Peptide, VirusBatch, Virus, AntibodyBatch, Antibody, Step, ProcessStep, Complex, ComplexBatch, Study, \
    RawDoc
from django.forms import formset_factory, inlineformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
from django.core.urlresolvers import reverse


from django.db.models import Max
import json

@login_required
def upload_file_study(request,pk):
    if request.method == 'POST':
        study = get_object_or_404(Study, id=pk)
        form = RawDocForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = RawDoc(file=form.cleaned_data['file'],
                              sid=request.FILES['file'].name)
            new_file.save()

            study.files.add(new_file)
            return redirect(request.META['HTTP_REFERER'])

@login_required
def upload_file_measurement(request,pk):
    if request.method == 'POST':
        raw_spot_collection = get_object_or_404(RawSpotCollection, id=pk)
        form = RawDocForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = RawDoc(file=form.cleaned_data['file'],
                              sid=request.FILES['file'].name)
            new_file.save()

            raw_spot_collection.files.add(new_file)
            return redirect(request.META['HTTP_REFERER'])

@login_required
def study_view(request,pk):
    study = get_object_or_404(Study, id=pk)
    if request.method == 'POST':
        status = request.POST.get("status")
        study.status = status
        study.save()

        return redirect(request.META['HTTP_REFERER'])

    else:

        collections = study.rawspotcollection_set.all()
        form = StudyForm(instance=study)
        form_rawdoc = RawDocForm()

        context = {
            'collections': collections,
            'study': study,
            'form': form,
            'form_rawdoc': form_rawdoc,
            'type': "measurement",

        }

    return render(request,
                  'flutype/study.html', context)

@login_required
def study_ligands_view(request,pk):
    study = get_object_or_404(Study, id=pk)
    if request.method == 'POST':
        status = request.POST.get("status")
        study.status = status
        study.save()
        for key in request.POST:
            print(key)
            value = request.POST[key]
            print(value)


        return redirect(request.META['HTTP_REFERER'])

    else:

        collections = study.rawspotcollection_set.all()
        viruses1 = Virus.objects.filter(ligands1__studies=study)
        viruses2 = Virus.objects.filter(ligands2__studies=study)

        peptides1 = Peptide.objects.filter(ligands1__studies=study)
        peptides2 = Peptide.objects.filter(ligands2__studies=study)

        antibodies1 = Antibody.objects.filter(ligands1__studies=study)
        antibodies2 = Antibody.objects.filter(ligands2__studies=study)

        complexes1 = Complex.objects.filter(ligands1__studies=study)
        complexes2 = Complex.objects.filter(ligands2__studies=study)

        #viruses1 = Virus.objects.filter(ligands1__studies =

        form = StudyForm(instance=study)
        form_rawdoc = RawDocForm()

        context = {
            'collections': collections,
            'study': study,
            'form': form,
            'form_rawdoc': form_rawdoc,
            'type': "ligands",
            'viruses1': viruses1,
            'viruses2': viruses2,
            'peptides1': peptides1,
            'peptides2': peptides2,
            'antibodies1': antibodies1,
            'antibodies2': antibodies2,
            'complexes1': complexes1,
            'complexes2': complexes2,


        }

    return render(request,
                  'flutype/study.html', context)


@login_required
def index_view(request):
    studies = Study.objects.filter(hidden=False)

    context = {
        'type': 'all',
        'studies': studies,
    }
    return render(request,
                  'flutype/index.html', context)


@login_required
def my_index_view(request):
    studies = Study.objects.filter(rawspotcollection__processstep__user=request.user, hidden=False).distinct()
    context = {
        'type': 'my',
        'studies': studies,
    }
    return render(request,
                  'flutype/index.html', context)

@login_required
def measurement_view(request, pk):
    """ Renders detailed RawSpotCollection View. """

    collection = get_object_or_404(RawSpotCollection, id=pk)

    if request.method == 'POST':
        status = request.POST.get("status")
        collection.status = status
        collection.save()

        return redirect(request.META['HTTP_REFERER'])

    else:

        form = MeasurementForm(instance=collection)
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
            'type': 'process',
            'collection': collection,
            'data': json.dumps(data),
            'row_list': json.dumps(row_list),
            'column_list': json.dumps(column_list),
            'form':form
        }
        return render(request,
                      'flutype/measurement.html', context)
@login_required
def measurement_ligands_view(request, pk):
    """ Renders detailed RawSpotCollection View. """

    collection = get_object_or_404(RawSpotCollection, id=pk)

    if request.method == 'POST':
        status = request.POST.get("status")
        collection.status = status
        collection.save()

        return redirect(request.META['HTTP_REFERER'])

    else:

        form = MeasurementForm(instance=collection)
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
            'type': 'ligands',
            'collection': collection,
            'data': json.dumps(data),
            'row_list': json.dumps(row_list),
            'column_list': json.dumps(column_list),
            'form':form
        }
        return render(request,
                      'flutype/measurement.html', context)



@login_required
def tutorial_db_view(request):
    """ Renders detailed RawSpotCollection View. """
    study = get_object_or_404(Study, sid="170929-tutorial")
    return study_view(request, study.id)





@login_required
def measurements_view(request):
    collections = RawSpotCollection.objects.filter(hidden=False)
    context = {
        'type': 'all',
        'collections': collections,
    }
    return render(request,
                  'flutype/measurements.html', context)



@login_required
def my_measurements_view(request):
    collections = RawSpotCollection.objects.filter(processstep__user=request.user, hidden=False).distinct()
    context = {
        'type': 'my',
        'collections': collections,
    }
    return render(request,
                  'flutype/measurements.html', context)


@login_required
def raw_spot_collection(request, pk):
    """ Renders detailed RawSpotCollection View. """

    collection = get_object_or_404(RawSpotCollection, id=pk)

    if request.method == 'POST':
        form = MeasurementForm(request.POST,  instance=collection)
        if form.is_valid():
            form.save()
        return redirect(request.META['HTTP_REFERER'])

    else:

        form = MeasurementForm(instance=collection)
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
            'form':form
        }
        return render(request,
                      'flutype/spotcollection.html', context)


@login_required
def quantified_spot_collection(request, pk):
    """ Renders detailed SpotCollection View. """

    sc = get_object_or_404(SpotCollection, id=pk)
    collection = sc.raw_spot_collection

    spots = sc.spot_set.all()

    row_max = spots.aggregate(Max('raw_spot__row'))
    column_max = spots.aggregate(Max('raw_spot__column'))

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
def processes_view(request):
    processes = Process.objects.all()

    context = {
        'processes': processes,
    }
    return render(request,
                  'flutype/processes.html', context)


@login_required
def process_view(request, pk):
    process = get_object_or_404(Process, id=pk)

    context = {
        'process': process,
    }
    return render(request,
                  'flutype/process.html', context)



@login_required
def users_view(request):
    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request,
                  'flutype/users.html', context)


def about_en_view(request):

    return render(request, "flutype/about.html", {"language": "en"})


def about_de_view(request):
    return render(request, "flutype/about.html", {"language": "de"})

@login_required
def database_scheme_en_view(request):
    return render(request, "flutype/database_scheme.html", {"language": "en"})

@login_required
def database_scheme_de_view(request):
    return render(request, "flutype/database_scheme.html", {"language": "de"})

@login_required
def tutorial_en_view(request):
    path_tutorial = os.path.join(BASE_DIR,"master_test/studies")
    generate_tree(path_tutorial)

    return render(request, "flutype/tutorial.html", {"language": "en"})

@login_required
def tutorial_de_view(request):
    return render(request, "flutype/tutorial.html", {"language": "de"})

@login_required
def tutorial_tree_view(request):
    return render(request, "flutype/tree.html")



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
    peptide_batches = PeptideBatch.objects.filter(lig_mob_batch__isnull=False).distinct()
    context = {
        'type': "mobile",
        'peptide_batches': peptide_batches,
    }
    return render(request,
                  'flutype/peptidebatches.html', context)


@login_required
def peptide_batch_fixed_view(request):
    peptide_batches = PeptideBatch.objects.filter(lig_fix_batch__isnull=False).distinct()
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
    virus_batches = VirusBatch.objects.filter(lig_mob_batch__isnull=False).distinct()
    context = {

        'type': "mobile",
        'virus_batches': virus_batches,
    }
    return render(request,
                  'flutype/virusbatches.html', context)


@login_required
def virus_batch_fixed_view(request):
    virus_batches = VirusBatch.objects.filter(lig_fix_batch__isnull=False).distinct()
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
    antibody_batches = AntibodyBatch.objects.filter(lig_mob_batch__isnull=False).distinct()
    context = {
        'type': "mobile",

        'antibody_batches': antibody_batches,
    }
    return render(request,
                  'flutype/antibodybatches.html', context)


@login_required
def antibody_batch_fixed_view(request):
    antibody_batches = AntibodyBatch.objects.filter(lig_fix_batch__isnull=False).distinct()
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
def highcharts_view(request, pk):
    sc = get_object_or_404(SpotCollection, id=pk)
    spots = sc.spot_set.all()
    row_max = spots.aggregate(Max('raw_spot__row'))
    column_max = spots.aggregate(Max('raw_spot__column'))

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
        'row_list': json.dumps(row_list),
        'column_list': json.dumps(column_list),
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
        return render(request, 'flutype/create.html', {'form': form, 'type': 'peptide'})

@login_required
def complex_view(request):
    complexes = Complex.objects.all()
    context = {
        'complexes': complexes,
    }
    return render(request,
                  'flutype/complexes.html', context)


@login_required
def complex_mobile_view(request):
    complexes = Complex.objects.filter(ligands2__isnull=False).distinct()
    context = {
        'type': "mobile",
        'complexes': complexes,
    }
    return render(request,
                  'flutype/complexes.html', context)


@login_required
def complex_fixed_view(request):
    complexes = Complex.objects.filter(ligands1__isnull=False).distinct()

    context = {
        'type': "fixed",
        'complexes': complexes,
    }
    return render(request,
                  'flutype/complexes.html', context)


@login_required
def complex_new(request):
    if request.method == 'POST':
        form = ComplexForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('complexes')
    else:
        form = ComplexForm()
        return render(request, 'flutype/create.html', {'form': form, 'type': 'complex'})

@login_required
def complex_delete(request, pk):
    complex = get_object_or_404(Complex, pk=pk)
    if request.method == 'POST':
        complex.delete()
        return redirect('peptides')
    return render(request, 'flutype/delete.html', {'complex': complex, 'type': 'complex'})


@login_required
def complex_edit(request, pk):
    instance = get_object_or_404(Complex, pk=pk)
    if request.method == 'POST':
        form = ComplexForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('complexes')
    else:
        form = ComplexForm(instance=instance)
        return render(request, 'flutype/create.html', {'form': form, 'type': 'complex'})

@login_required
def complex_batch_delete(request, pk):
    complex_batch = get_object_or_404(ComplexBatch, pk=pk)
    if request.method == 'POST':
        complex_batch.delete()
        return redirect('complexbatches')
    return render(request, 'flutype/delete.html', {'complex_batch': complex_batch, 'type': 'complex_batch'})

@login_required
def complex_batch_edit(request, pk):
    instance = get_object_or_404(ComplexBatch, pk=pk)
    if request.method == 'POST':
        form = ComplexBatchForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('complexbatches')
    else:
        form = ComplexBatchForm(instance=instance)
        return render(request, 'flutype/create.html', {'form': form, 'type': 'complex_batch'})

@login_required
def complex_batch_new(request):
    if request.method == 'POST':
        form = ComplexBatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('complexbatches')
    else:
        form = ComplexBatchForm()
        return render(request, 'flutype/create.html', {'form': form, 'type': 'complex_batch'})

@login_required
def complex_batch_view(request):
    complex_batches = ComplexBatch.objects.all()
    context = {
        'complex_batches': complex_batches,
    }
    return render(request,
                  'flutype/complexbatches.html', context)


@login_required
def complex_batch_mobile_view(request):
    complex_batches = ComplexBatch.objects.filter(lig_mob_batch__isnull=False).distinct()
    context = {
        'type': "mobile",
        'complex_batches': complex_batches,
    }
    return render(request,
                  'flutype/complexbatches.html', context)


@login_required
def complex_batch_fixed_view(request):
    complex_batches = ComplexBatch.objects.filter(lig_fix_batch__isnull=False).distinct()
    context = {
        'type': "fixed",
        'complex_batches': complex_batches,
    }
    return render(request,
                  'flutype/complexbatches.html', context)


@login_required
def virus_new(request):
    if request.method == 'POST':
        form = VirusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('viruses')
    else:
        form = VirusForm()
        return render(request, 'flutype/create.html', {'form': form, 'type': 'virus'})


@login_required
def antibody_new(request):
    if request.method == 'POST':
        form = VirusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('antibodies')
    else:
        form = AntibodyForm()
        return render(request, 'flutype/create.html', {'form': form, 'type': 'antibody'})


@login_required
def peptide_edit(request, pk):
    instance = get_object_or_404(Peptide, pk=pk)
    if request.method == 'POST':
        form = PeptideForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('peptides')
    else:
        form = PeptideForm(instance=instance)
        return render(request, 'flutype/create.html', {'form': form, 'type': 'peptide'})


@login_required
def virus_edit(request, pk):
    instance = get_object_or_404(Virus, pk=pk)
    if request.method == 'POST':
        form = VirusForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('viruses')
    else:
        form = VirusForm(instance=instance)
        return render(request, 'flutype/create.html', {'form': form, 'type': 'virus'})


@login_required
def antibody_edit(request, pk):
    instance = get_object_or_404(Antibody, pk=pk)
    if request.method == 'POST':
        form = AntibodyForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('antibodies')
    else:

        form = AntibodyForm(instance=instance)
        return render(request, 'flutype/create.html', {'form': form, 'type': 'antibody'})


@login_required
def peptide_delete(request, pk):
    peptide = get_object_or_404(Peptide, pk=pk)
    if request.method == 'POST':
        peptide.delete()
        return redirect('peptides')
    return render(request, 'flutype/delete.html', {'peptide': peptide, 'type': 'peptide'})


@login_required
def virus_delete(request, pk):
    virus = get_object_or_404(Virus, pk=pk)
    if request.method == 'POST':
        virus.delete()
        return redirect('viruses')
    return render(request, 'flutype/delete.html', {'virus': virus, 'type': 'virus'})


@login_required
def antibody_delete(request, pk):
    antibody = get_object_or_404(Antibody, pk=pk)
    if request.method == 'POST':
        antibody.delete()
        return redirect('antibodies')
    return render(request, 'flutype/delete.html', {'antibody': antibody, 'type': 'antibody'})


@login_required
def antibody_batch_delete(request, pk):
    antibody_batch = get_object_or_404(AntibodyBatch, pk=pk)
    if request.method == 'POST':
        antibody_batch.delete()
        return redirect('antibodybatches')
    return render(request, 'flutype/delete.html', {'antibody_batch': antibody_batch, 'type': 'antibody_batch'})


@login_required
def peptide_batch_delete(request, pk):
    peptide_batch = get_object_or_404(PeptideBatch, pk=pk)
    if request.method == 'POST':
        peptide_batch.delete()
        return redirect('peptidebatches')
    return render(request, 'flutype/delete.html', {'peptide_batch': peptide_batch, 'type': 'peptide_batch'})


@login_required
def virus_batch_delete(request, pk):
    virus_batch = get_object_or_404(VirusBatch, pk=pk)
    if request.method == 'POST':
        virus_batch.delete()
        return redirect('virusbatches')
    return render(request, 'flutype/delete.html', {'virus_batch': virus_batch, 'type': 'virus_batch'})


@login_required
def antibody_batch_edit(request, pk):
    instance = get_object_or_404(AntibodyBatch, pk=pk)
    if request.method == 'POST':
        form = AntibodyBatchForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('antibodybatches')
    else:
        form = AntibodyBatchForm(instance=instance)
        return render(request, 'flutype/create.html', {'form': form, 'type': 'antibody_batch'})


@login_required
def virus_batch_edit(request, pk):
    instance = get_object_or_404(VirusBatch, pk=pk)
    if request.method == 'POST':
        form = VirusBatchForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('virusbatches')
    else:
        form = VirusBatchForm(instance=instance)
        return render(request, 'flutype/create.html', {'form': form, 'type': 'virus_batch'})


@login_required
def peptide_batch_edit(request, pk):
    instance = get_object_or_404(PeptideBatch, pk=pk)
    if request.method == 'POST':
        form = PeptideBatchForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('peptidebatches')
    else:
        form = PeptideBatchForm(instance=instance)
        return render(request, 'flutype/create.html', {'form': form, 'type': 'peptide_batch'})


@login_required
def peptide_batch_new(request):
    if request.method == 'POST':
        form = PeptideBatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('peptidebatches')
    else:
        form = PeptideBatchForm()
        return render(request, 'flutype/create.html', {'form': form, 'type': 'peptide_batch'})


@login_required
def virus_batch_new(request):
    if request.method == 'POST':
        form = VirusBatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('virusbatches')
    else:
        form = VirusBatchForm()
        return render(request, 'flutype/create.html', {'form': form, 'type': 'virus_batch'})


@login_required
def antibody_batch_new(request):
    if request.method == 'POST':
        form = AntibodyBatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('antibodybatches')
    else:
        form = AntibodyBatchForm()
        return render(request, 'flutype/create.html', {'form': form, 'type': 'antibody_batch'})


@login_required
def steps_view(request):
    steps = Step.objects.all()
    context = {
        'steps': steps,
    }
    return render(request,
                  'flutype/process_steps.html', context)


@login_required
def step_new(request, class_name):
    if request.method == 'POST':

        form = eval("{}Form(request.POST)".format(class_name))
        if form.is_valid():
            form.save()
            return redirect('steps')
    else:
        form = eval("{}Form()".format(class_name))
        return render(request, 'flutype/create.html', {'form': form, 'type': 'step', "class": class_name})


@login_required
def step_edit(request, pk):
    instance = get_object_or_404(Step, pk=pk)
    instance = instance.get_step_type
    if request.method == 'POST':
        form = eval("{}Form(request.POST,instance=instance)".format(instance.__class__.__name__))
        if form.is_valid():
            form.save()
            return redirect('steps')
    else:
        form = eval("{}Form(instance=instance)".format(instance.__class__.__name__))
        return render(request, 'flutype/create.html',
                      {'form': form, 'type': 'step', 'class': instance.__class__.__name__})


@login_required
def step_delete(request, pk):
    step = get_object_or_404(Step, pk=pk)
    if request.method == 'POST':
        step.delete()
        return redirect('steps')
    return render(request, 'flutype/delete.html', {'step': step, 'type': 'step'})


@login_required
def process_new(request):
    Steps2FormSet = inlineformset_factory(Process, ProcessStep, form=ProcessStepForm, extra=0, can_delete=True)

    if request.method == 'POST':

        formset = Steps2FormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                print(form.step)
                # todo not redirect but load process data. add button to go back to process

            return redirect('processes')
    else:
        formset = Steps2FormSet()
        return render(request, 'flutype/create_process.html', {'formset': formset, 'type': 'process'})



@login_required
def image_view(request, pk):
    rsc = get_object_or_404(RawSpotCollection, pk=pk)
    return render(request, 'flutype/show_image.html', {'image': rsc.image_90_big})

@login_required
def image_process_view(request, pk):
    ps = get_object_or_404(ProcessStep, pk=pk)
    return render(request, 'flutype/show_image.html', {'image': ps.image_90_big})

@login_required
@api_view(['GET'])
def barplot_data_view(request, pk):
    sc = get_object_or_404(SpotCollection, id=pk)
    all_spots = sc.spot_set.all()
    spot_lig1 = all_spots.values_list("raw_spot__lig_fix_batch__sid", flat=True)
    lig1 = spot_lig1.distinct()
    box_list = []
    for lig in lig1:
        a = {}
        a["intensity"] = all_spots.filter(raw_spot__lig_fix_batch__sid=lig).values_list("intensity", flat=True)
        a["lig2"] = all_spots.filter(raw_spot__lig_fix_batch__sid=lig).values_list("raw_spot__lig_mob_batch__sid", flat=True)
        a["lig1"] = all_spots.filter(raw_spot__lig_fix_batch__sid=lig).values_list("raw_spot__lig_fix_batch__ligand__sid").first()
        a["lig1_con"] = all_spots.filter(raw_spot__lig_fix_batch__sid=lig).values_list(
            "raw_spot__lig_fix_batch__concentration").first()
        box_list.append(a)
    data = {
        "box_list": box_list,
        "lig1": lig1,
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

