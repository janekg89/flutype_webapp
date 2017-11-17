# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User

from .helper import generate_tree, tar_tree, empty_list
from .forms import PeptideForm, VirusForm, AntibodyForm, AntibodyBatchForm, \
    PeptideBatchForm, VirusBatchForm, ProcessStepForm, ComplexBatchForm, ComplexForm, StudyForm, \
    WashingForm,DryingForm,SpottingForm, QuenchingForm,BlockingForm,IncubatingForm, \
    ScanningForm, IncubatingAnalytForm, RawDocForm, BufferForm, BufferBatchForm, GalFileForm
from .models import RawSpotCollection, SpotCollection, Process, PeptideBatch, \
    Peptide, VirusBatch, Virus, AntibodyBatch, Antibody, Step, ProcessStep, Complex, ComplexBatch, Study, \
    RawDoc , Buffer, BufferBatch
from django.forms import formset_factory, inlineformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.timezone import localtime, now
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


from django.db.models import Max
import json
from flutype import __version__


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
def gal_file_view(request):
    type="start"
    form = GalFileForm()
    context = {
        "type":type,
        "form":form,
    }
    if request.method == 'POST':
        form = GalFileForm(request.POST, request.FILES)
        context["form"] =form
        if "exisiting_gal" in request.POST:
            context["type"] ="edit"
        elif "new_gal" in request.POST:
            context["type"]="detail"
        elif "update" in request.POST:
            context["type"] = "detail"
            if form.is_valid():
                model_instance = form.save(commit=False)
                context["gal_file"]=model_instance
                context["grid"]= json.dumps(model_instance.create_gal_file_base().tolist())
                context["tray"]= json.dumps(model_instance.create_tray_base().tolist())
                context["form"]= form



    return render(request, 'flutype/create_gal.html', context)

def raw_gal_file_view(request):
    antibody_batches = AntibodyBatch.objects.all()
    peptide_batches = PeptideBatch.objects.all()
    virus_batches = VirusBatch.objects.all()
    complex_batches = ComplexBatch.objects.all()
    buffer_batches = BufferBatch.objects.all()

    context = {
        'type':"gal_file",
        'antibody_batches': antibody_batches,
        'peptide_batches': peptide_batches,
        'virus_batches': virus_batches,
        'complex_batches': complex_batches,
        'buffer_batches': buffer_batches,

    }
    return render(request,
                  'flutype/create_raw_gal.html', context)


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
def study_view(request,sid):
    study = get_object_or_404(Study, sid=sid)
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

    return render(request, 'flutype/study.html', context)


@login_required
def study_ligands_view(request,sid):
    study = get_object_or_404(Study, sid=sid)
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

    return render(request, 'flutype/study.html', context)


@login_required
def studies_view(request):
    #
    #studies = Study.objects.filter(hidden=False)
    studies = Study.objects.all()

    context = {
        'type': 'all',
        'studies': studies,
    }
    return render(request,
                  'flutype/studies.html', context)


@login_required
def my_studies_view(request):
    studies = Study.objects.filter(rawspotcollection__processstep__user=request.user, hidden=False).distinct()
    context = {
        'type': 'my',
        'studies': studies,
    }
    return render(request,
                  'flutype/studies.html', context)


@login_required
def measurement_view(request, sid):
    """ Renders detailed RawSpotCollection View. """

    collection = get_object_or_404(RawSpotCollection, sid=sid)
    context = {

        'type': 'process',
        'collection': collection,
    }
    return render(request,
                  'flutype/measurement.html', context)
@login_required
def measurement_ligands_view(request, sid):
    """ Renders detailed RawSpotCollection View. """
    collection = get_object_or_404(RawSpotCollection, sid=sid)
    context = {
        'type': 'ligands',
        'collection': collection,
    }
    return render(request,
                  'flutype/measurement.html', context)

@login_required
def measurement_result_view(request, measurement_sid ,sid):
    """ Renders detailed RawSpotCollection View. """
    collection = get_object_or_404(RawSpotCollection, sid=measurement_sid)
    sc = collection.spotcollection_set.get(sid=sid)
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



    context = {
        'lig1': json.dumps(collection.pivot_ligand1().values.tolist()),
        'lig2': json.dumps(collection.pivot_ligand2().values.tolist()),
        'con1': json.dumps(collection.pivot_concentration1().values.tolist()),
        'con2': json.dumps(collection.pivot_concentration2().values.tolist()),
        'type': 'quantified',
        'collection': collection,
        'q_collection': sc,
        'data': json.dumps(data),
        'row_list': json.dumps(row_list),
        'column_list': json.dumps(column_list),
        }
    return render(request,
                      'flutype/measurement.html', context)


@login_required
def tutorial_db_view(request):
    """ Renders detailed RawSpotCollection View. """
    study = get_object_or_404(Study, sid="170929-tutorial")
    return study_view(request, study.sid)


@login_required
def glossary_view(request):

    return render(request, "flutype/glossary.html", {"language": "en"})


@login_required
def measurements_view(request):
    #collections = RawSpotCollection.objects.filter(hidden=False)
    collections = RawSpotCollection.objects.all()

    context = {
        'type': 'all',
        'collections': collections,
    }
    return render(request,
                  'flutype/measurements.html', context)



@login_required
def my_measurements_view(request):
    #collections = RawSpotCollection.objects.filter(processstep__user=request.user, hidden=False).distinct()
    collections = RawSpotCollection.objects.filter(processstep__user=request.user).distinct()

    context = {
        'type': 'my',
        'collections': collections,
    }
    return render(request,
                  'flutype/measurements.html', context)


@login_required
def raw_spot_collection(request, sid):
    """ Renders detailed RawSpotCollection View. """

    collection = get_object_or_404(RawSpotCollection, sid=sid)

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
def quantified_spot_collection(request, sid):
    """ Renders detailed SpotCollection View. """

    sc = get_object_or_404(SpotCollection, sid=sid)
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
        'lig1': json.dumps(collection.pivot_ligand1().values.tolist()),
        'lig2': json.dumps(collection.pivot_ligand2().values.tolist()),
        'con1': json.dumps(collection.pivot_concentration1().values.tolist()),
        'con2': json.dumps(collection.pivot_concentration2().values.tolist()),
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
def process_view(request, sid):
    process = get_object_or_404(Process, sid=sid)

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
    return render(request, "flutype/about.html",
                  {
                      "language": "en",
                      "version": __version__,
                  })

def about_de_view(request):
    return render(request, "flutype/about.html",
                  {
                      "language": "de",
                      "version": __version__,
                  })


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
def buffer_view(request):
    buffers = Buffer.objects.all()
    context = {

        'buffers': buffers,
    }
    return render(request,
                  'flutype/buffers.html', context)

@login_required
def buffer_new(request):
    form = BufferForm()
    if request.method == 'POST':
        form = BufferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('buffers')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'buffer'})

@login_required
def buffer_edit(request, sid):
    instance = get_object_or_404(Buffer, sid=sid)
    form = BufferForm(instance=instance)
    if request.method == 'POST':
        form = BufferForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('buffers')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'buffer'})


@login_required
def buffer_batch_view(request):
    buffer_batches = BufferBatch.objects.all()
    context = {

        'buffer_batches': buffer_batches,
    }
    return render(request,
                  'flutype/bufferbatches.html', context)

# TODO: create one ligand create and edit view

@login_required
def buffer_batch_new(request):
    form = BufferBatchForm(initial={'produced_by': request.user, 'production_date': localtime(now()).date()})
    if request.method == 'POST':
        form = BufferBatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bufferbatches')

    return render(request, 'flutype/create.html', {'form': form, 'type': 'buffer_batch'})

@login_required
def buffer_batch_edit(request, sid):
    instance = get_object_or_404(BufferBatch, sid=sid)
    form = BufferBatchForm(instance=instance)
    if request.method == 'POST':
        form = BufferBatchForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('bufferbatches')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'buffer_batch'})


@login_required
def highcharts_view(request, measurement_sid,sid):
    collection = get_object_or_404(RawSpotCollection, sid=measurement_sid)
    sc = collection.spotcollection_set.get(sid=sid)
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
    form = PeptideForm()
    if request.method == 'POST':
        form = PeptideForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('peptides')
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
    form = ComplexForm()
    if request.method == 'POST':
        form = ComplexForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('complexes')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'complex'})

@login_required
def complex_delete(request, sisd):
    complex = get_object_or_404(Complex, sisd=sisd)
    if request.method == 'POST':
        complex.delete()
        return redirect('peptides')
    return render(request, 'flutype/delete.html', {'complex': complex, 'type': 'complex'})


@login_required
def complex_edit(request, sid):
    instance = get_object_or_404(Complex, sid=sid)
    form = ComplexForm(instance=instance)
    if request.method == 'POST':
        form = ComplexForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('complexes')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'complex'})

@login_required
def complex_batch_delete(request, sid):
    complex_batch = get_object_or_404(ComplexBatch, sid=sid)
    if request.method == 'POST':
        complex_batch.delete()
        return redirect('complexbatches')
    return render(request, 'flutype/delete.html', {'complex_batch': complex_batch, 'type': 'complex_batch'})

@login_required
def complex_batch_edit(request, sid):
    instance = get_object_or_404(ComplexBatch, sid=sid)
    form = ComplexBatchForm(instance=instance)

    if request.method == 'POST':
        form = ComplexBatchForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('complexbatches')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'complex_batch'})

@login_required
def complex_batch_new(request):
    form = ComplexBatchForm(initial={'produced_by': request.user, 'production_date': localtime(now()).date()}
                            )
    if request.method == 'POST':
        form = ComplexBatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('complexbatches')
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
    form = VirusForm()
    if request.method == 'POST':
        form = VirusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('viruses')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'virus'})


@login_required
def antibody_new(request):
    form = AntibodyForm()
    if request.method == 'POST':
        form = AntibodyForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            return redirect('antibodies')
    form = AntibodyForm()
    return render(request, 'flutype/create.html', {'form': form, 'type': 'antibody'})


@login_required
def peptide_edit(request, sid):
    instance = get_object_or_404(Peptide, sid=sid)
    form = PeptideForm(instance=instance)
    if request.method == 'POST':
        form = PeptideForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('peptides')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'peptide'})


@login_required
def virus_edit(request, sid):
    instance = get_object_or_404(Virus, sid=sid)
    form = VirusForm(instance=instance)
    if request.method == 'POST':
        form = VirusForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('viruses')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'virus'})


@login_required
def antibody_edit(request, sid):

    instance = get_object_or_404(Antibody, sid=sid)
    form = AntibodyForm(instance=instance)

    if request.method == 'POST':
        form = AntibodyForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('antibodies')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'antibody'})


@login_required
def peptide_delete(request, sid):
    peptide = get_object_or_404(Peptide, sid=sid)
    if request.method == 'POST':
        peptide.delete()
        return redirect('peptides')
    return render(request, 'flutype/delete.html', {'peptide': peptide, 'type': 'peptide'})


@login_required
def virus_delete(request, sid):
    virus = get_object_or_404(Virus, sid=sid)
    if request.method == 'POST':
        virus.delete()
        return redirect('viruses')
    return render(request, 'flutype/delete.html', {'virus': virus, 'type': 'virus'})


@login_required
def antibody_delete(request, sid):
    antibody = get_object_or_404(Antibody, sid=sid)
    if request.method == 'POST':
        antibody.delete()
        return redirect('antibodies')
    return render(request, 'flutype/delete.html', {'antibody': antibody, 'type': 'antibody'})


@login_required
def antibody_batch_delete(request, sid):
    antibody_batch = get_object_or_404(AntibodyBatch, sid=sid)
    if request.method == 'POST':
        antibody_batch.delete()
        return redirect('antibodybatches')
    return render(request, 'flutype/delete.html', {'antibody_batch': antibody_batch, 'type': 'antibody_batch'})


@login_required
def peptide_batch_delete(request, sid):
    peptide_batch = get_object_or_404(PeptideBatch, sid=sid)
    if request.method == 'POST':
        peptide_batch.delete()
        return redirect('peptidebatches')
    return render(request, 'flutype/delete.html', {'peptide_batch': peptide_batch, 'type': 'peptide_batch'})


@login_required
def virus_batch_delete(request, sid):
    virus_batch = get_object_or_404(VirusBatch, sid=sid)
    if request.method == 'POST':
        virus_batch.delete()
        return redirect('virusbatches')
    return render(request, 'flutype/delete.html', {'virus_batch': virus_batch, 'type': 'virus_batch'})


@login_required
def antibody_batch_edit(request, sid):
    instance = get_object_or_404(AntibodyBatch, sid=sid)
    form = AntibodyBatchForm(instance=instance)

    if request.method == 'POST':
        form = AntibodyBatchForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('antibodybatches')

    return render(request, 'flutype/create.html', {'form': form, 'type': 'antibody_batch'})


@login_required
def virus_batch_edit(request, sid):
    instance = get_object_or_404(VirusBatch, sid=sid)
    form = VirusBatchForm(instance=instance)

    if request.method == 'POST':
        form = VirusBatchForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('virusbatches')

    return render(request, 'flutype/create.html', {'form': form, 'type': 'virus_batch'})


@login_required
def peptide_batch_edit(request, sid):
    instance = get_object_or_404(PeptideBatch, sid=sid)
    form = PeptideBatchForm(instance=instance)
    if request.method == 'POST':
        form = PeptideBatchForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('peptidebatches')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'peptide_batch'})


@login_required
def peptide_batch_new(request):
    form = PeptideBatchForm(initial={'produced_by': request.user, 'production_date': localtime(now()).date()})
    if request.method == 'POST':
        form = PeptideBatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('peptidebatches')

    return render(request, 'flutype/create.html', {'form': form, 'type': 'peptide_batch'})


@login_required
def virus_batch_new(request):
    form = VirusBatchForm(initial={'produced_by': request.user, 'production_date': localtime(now()).date()})
    if request.method == 'POST':
        form = VirusBatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('virusbatches')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'virus_batch'})



@login_required
def antibody_batch_new(request):
    form = AntibodyBatchForm(initial={'produced_by': request.user, 'production_date': localtime(now()).date()}
                             )
    if request.method == 'POST':
        form = AntibodyBatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('antibodybatches')
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
    form = eval("{}Form()".format(class_name))
    if request.method == 'POST':

        form = eval("{}Form(request.POST)".format(class_name))
        if form.is_valid():
            form.save()
            return redirect('steps')
    return render(request, 'flutype/create.html', {'form': form, 'type': 'step', "class": class_name})


@login_required
def step_edit(request, sid):
    instance = get_object_or_404(Step, sid=sid)
    instance = instance.get_step_type
    form = eval("{}Form(instance=instance)".format(instance.__class__.__name__))
    if request.method == 'POST':
        form = eval("{}Form(request.POST,instance=instance)".format(instance.__class__.__name__))
        if form.is_valid():
            form.save()
            return redirect('steps')

    return render(request, 'flutype/create.html',
                      {'form': form, 'type': 'step', 'class': instance.__class__.__name__})


@login_required
def step_delete(request, sid):
    step = get_object_or_404(Step, sid=sid)
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
def image_view(request, sid):
    rsc = get_object_or_404(RawSpotCollection, sid=sid)
    return render(request, 'flutype/show_image.html', {'image': rsc.image_90_big})

@login_required
def image_process_view(request, id):
    ps = get_object_or_404(ProcessStep, id=id)
    return render(request, 'flutype/show_image.html', {'image': ps.image_90_big})

@login_required
@api_view(['GET'])
def barplot_data_view(request,measurement_sid, sid):
    collection = get_object_or_404(RawSpotCollection, sid=measurement_sid)
    sc = collection.spotcollection_set.get(sid=sid)
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

