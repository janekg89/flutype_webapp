# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.http import JsonResponse,HttpResponseForbidden,Http404
from .helper import generate_tree,  empty_list, auto_get_or_create_ligand_batches, \
    camel_case_split, filter_for_class
from .utils.utils_views import delete_posted_and_redirect, save_posted_and_redirect
from .forms import PeptideForm, VirusForm, AntibodyForm, AntibodyBatchForm, \
    PeptideBatchForm, VirusBatchForm, ProcessStepForm, ComplexBatchForm, ComplexForm, StudyForm, \
    WashingForm,DryingForm,SpottingForm, QuenchingForm,BlockingForm,IncubatingForm, \
    ScanningForm, IncubatingAnalytForm, RawDocForm, BufferForm, BufferBatchForm, GalFileForm, MeasurementForm
from .models import RawSpotCollection, SpotCollection, Process, PeptideBatch, \
    Peptide, VirusBatch, Virus, AntibodyBatch, Antibody, Step, ProcessStep, Complex, ComplexBatch, Study, \
    RawDoc , Buffer, BufferBatch, Ligand, UnitsType, LigandBatch, GalFile, Scanning
from django.forms import formset_factory, inlineformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from tempfile import NamedTemporaryFile
from django.apps import apps
from django.db import transaction
from guardian.shortcuts import assign_perm



#from guardian.decorators import permission_required_or_403

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import pandas as pd

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
def import_measurement_view(request,sid):
    study = get_object_or_404(Study, sid=sid)
    ligands_sid =  list(LigandBatch.objects.filter(stock=True).values_list("sid",flat=True).all())
    steps_sid =  list(Step.objects.values_list("sid",flat=True).all())
    scanning_sid =  list(Scanning.objects.values_list("sid",flat=True).all())
    user_names =  list(User.objects.values_list("username",flat=True).all())


    concentration_units = list(UnitsType.labels.values())
    measurement_form = MeasurementForm(initial={'user': request.user})
    if request.method == 'POST':
        if "measurement_type" in request.POST and not "ligands" in request.POST:
            measurement_form = MeasurementForm(request.POST)
            if measurement_form.errors:
                response = {"errors":measurement_form.errors, "is_error": True}
                return JsonResponse(response)

        else:
            python_version = sys.version_info.major
            if python_version == 3:
                body_unicode = request.body.decode('utf-8')
            else:
                body_unicode = request.body
            json_data = json.loads(body_unicode)
            #ligands related data
            data_ligands = json_data.get("ligands")
            ligand_batches = auto_get_or_create_ligand_batches(data_ligands)

            fix_gal_file = ligand_batches[['Row', 'Column', 'sid']]
            fix_gal_file["Block"] = 1
            fix_gal_file.rename(columns={"sid": "Name"}, inplace=True)
            fix_gal_file.index.names = ['ID']

            data_analyts = json_data.get("analyts")
            analyt_batches = auto_get_or_create_ligand_batches(data_analyts)
            mob_gal_file = analyt_batches[['Row', 'Column', 'sid']]
            mob_gal_file["Block"] = 1
            mob_gal_file.rename(columns={"sid": "Name"}, inplace=True)
            mob_gal_file.index.names = ['ID']

            data_results = json_data.get("intensities")
            data_results = pd.DataFrame(data_results, columns=range(1, 13), index=range(1, 9))

            data_process = json_data.get("process")

            data_process = pd.DataFrame(data_process,columns=["step","user","start date","start time","intensities","comment"])
            data_process["start"] = data_process["start date"]+" "+data_process["start time"]
            data_process["index"] = data_process.index
            data_process["image"] = None


            raw_spot_collection_dict = json_data.get("measurement")
            if raw_spot_collection_dict["user"] in ["",]:
                raw_spot_collection_dict["user"] = None
            else:
                raw_spot_collection_dict["user"] = User.objects.get(pk=raw_spot_collection_dict["user"])
            with NamedTemporaryFile() as temp_intensities:
                data_results.to_csv(temp_intensities.name, sep=str('\t'), index="True", encoding='utf-8')
                results_dic= {"raw":{"meta":{"sid":"raw"},"intensities":temp_intensities.name}}
                with NamedTemporaryFile() as temp_lig_fix:
                    fix_gal_file.to_csv(temp_lig_fix.name, sep=str('\t'), index="True", encoding='utf-8')
                    with NamedTemporaryFile() as temp_lig_mob:
                        mob_gal_file.to_csv(temp_lig_mob.name, sep=str('\t'), index="True", encoding='utf-8')
                        with NamedTemporaryFile() as temp_steps:
                            data_process["intensities"] = [None if step in ["", False, None] else temp_intensities.name for step in data_process["intensities"]]
                            data_process[["step","user","start","index","comment","intensities","image"]].to_csv(temp_steps.name, sep=str('\t'), encoding='utf-8')

                            #fixme: no process data, no raw_docs
                            # fixme: for edit this should be just the way around
                            if RawSpotCollection.objects.filter(sid=raw_spot_collection_dict["sid"]).exists():
                                return JsonResponse({"is_error":True, "msg":"measurement sid allready exists!"})



                            rsc,_ = RawSpotCollection.objects.get_or_create(results=results_dic,
                                                                            lig_mob_path=temp_lig_mob.name,
                                                                            lig_fix_path=temp_lig_fix.name,
                                                                            steps_path = temp_steps.name,
                                                                            meta = raw_spot_collection_dict,
                                                                            study=study)
            return JsonResponse({"is_error": False, "rsc_sid":rsc.sid})

            #return redirect("/measurement/"+rsc.sid)

            #spot related operations #fixme add in frontend validations of intensities, that a rawspot has to exisit before creating a spot !


        return JsonResponse({"is_error": False})

    else:

        collections = study.rawspotcollection_set.all()

        context = {
            'collections': collections,
            'study': study,
            'type': "measurement",
            'ligands_sid':ligands_sid,
            'steps_sid': steps_sid,
            'scanning_sid': scanning_sid,
            'user_names': user_names,
            'concentration_units': concentration_units,
            'measurement_form':measurement_form
        }

    return render(request, 'flutype/import_measurement.html', context)


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
    ligandbatch_types = ["AntibodyBatch","BufferBatch","ComplexBatch","PeptideBatch","VirusBatch"]


    fixed_ligandbatch_pks =collection.rawspot_set.values_list('lig_fix_batch', flat=True).distinct()
    fixed_ligandbatches = LigandBatch.objects.filter(pk__in = fixed_ligandbatch_pks).select_subclasses()
    #fixed_lig_batch = {ligand_batch_type:filter_for_class(fixed_ligandbatches,ligand_batch_type) for ligand_batch_type in ligandbatch_types}

    mobile_ligandbatch_pks = collection.rawspot_set.values_list('lig_mob_batch', flat=True).distinct()
    mobile_ligandbatches = LigandBatch.objects.filter(pk__in=mobile_ligandbatch_pks).select_subclasses()
    #mobile_lig_batch = {ligand_batch_type:filter_for_class(mobile_ligandbatches,ligand_batch_type) for ligand_batch_type in ligandbatch_types}


    context = {
        'mobile_lig_batch': mobile_ligandbatches,
        'fixed_lig_batch': fixed_ligandbatches,
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
    peptide_batches_all = PeptideBatch.objects.all()
    peptide_batches = peptide_batches_all.filter(stock=True)
    context = {
        'peptide_batches_all': peptide_batches_all,
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
def virus_batch_view(request):
    virus_batches_all = VirusBatch.objects.all()
    virus_batches = virus_batches_all.filter(stock=True)
    context = {
        'virus_batches_all':virus_batches_all,
        'virus_batches': virus_batches,
    }
    return render(request,
                  'flutype/virusbatches.html', context)


@login_required
def antibody_batch_view(request):
    antibody_batches_all = AntibodyBatch.objects.all()
    antibody_batches = antibody_batches_all.filter(stock=True)
    context = {
        'antibody_batches_all':antibody_batches_all,
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
def virus_view(request):
    viruses = Virus.objects.all()
    context = {

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
def buffer_batch_view(request):
    buffer_batches_all = BufferBatch.objects.all()
    buffer_batches = buffer_batches_all.filter(stock=True)
    context = {
        'buffer_batches_all':buffer_batches_all,
        'buffer_batches': buffer_batches,
    }
    return render(request,
                  'flutype/bufferbatches.html', context)

# TODO: create one ligand create and edit view



@login_required
def study_edit(request,pk):
    instance = get_object_or_404(Study, pk=pk)
    perm = request.user.has_perm('change_study',instance)
    print(perm)
    if not perm:
        return HttpResponseForbidden()

    form = StudyForm(instance=instance)
    if request.method == 'POST':
        form =  StudyForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('index')
    return render(request, 'flutype/create.html', {'form': form,})

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
def complex_view(request):
    complexes = Complex.objects.all()
    context = {
        'complexes': complexes,
    }
    return render(request,
                  'flutype/complexes.html', context)



@login_required
def complex_batch_view(request):
    complex_batches = ComplexBatch.objects.all()
    context = {
        'complex_batches': complex_batches,
    }
    return render(request,
                  'flutype/complexbatches.html', context)

@login_required
def new_view(request,model_name,**kwargs):
    Model = apps.get_model("flutype",model_name)
    Form = Model.get_form()
    form_instance = Form(**kwargs)
    if request.method == 'POST':
        form_instance = Form(request.POST,**kwargs)
        if form_instance.is_valid():
            return save_posted_and_redirect(form_instance)
    return render(request, 'flutype/create.html', {'form': form_instance})

@login_required
def edit_view(request, model_name, pk):
    Model = apps.get_model("flutype", model_name)
    instance = get_object_or_404(Model, pk=pk)
    forms_dict = {"instance": instance}
    return new_view(request, model_name, **forms_dict)

@login_required
def study_new(request):
    Model = apps.get_model("flutype", "Study")
    Form = Model.get_form()
    form_instance = Form(initial={"user":request.user})
    if request.method == 'POST':
        form_instance = Form(request.POST)
        if form_instance.is_valid():
            study_instance = form_instance.save()
            assign_perm("change_study", study_instance.user, study_instance)
            assign_perm("delete_study", study_instance.user, study_instance)
            return redirect(form_instance.url_redirect)
    return render(request, 'flutype/create.html', {'form': form_instance})

@login_required
def ligandbatch_new(request, model_name):
    forms_dict = {"initial":{"produced_by":request.user}}
    return new_view(request,model_name,**forms_dict)

@login_required
def delete_view(request, model_name, pk):
    Model = apps.get_model("flutype", model_name)
    instance = get_object_or_404(Model, pk=pk)
    if request.method == 'POST':
        return delete_posted_and_redirect(instance)
    return render(request, 'flutype/delete.html', {'instance':instance})


@login_required
def steps_view(request):
    steps = Step.objects.all()
    context = {
        'steps': steps,
    }
    return render(request,
                  'flutype/process_steps.html', context)

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
        a["lig1"] = lig
        a["lig1_con"] = all_spots.filter(raw_spot__lig_fix_batch__sid=lig).values_list(
            "raw_spot__lig_fix_batch__concentration").first()
        box_list.append(a)
    data = {
        "box_list": box_list,
        "lig1": lig1,
    }
    return Response(data)

@login_required
@api_view(['GET'])
def barplot2_data_view(request,measurement_sid, sid):
    collection = get_object_or_404(RawSpotCollection, sid=measurement_sid)
    sc = collection.spotcollection_set.get(sid=sid)
    all_spots = sc.spot_set.all()
    spot_lig1 = all_spots.values_list("raw_spot__lig_mob_batch__sid", flat=True)
    lig1 = spot_lig1.distinct()
    box_list = []
    print(lig1)
    for lig in lig1:
        a = {}
        a["intensity"] = all_spots.filter(raw_spot__lig_mob_batch__sid=lig).values_list("intensity", flat=True)
        a["lig2"] = all_spots.filter(raw_spot__lig_mob_batch__sid=lig).values_list("raw_spot__lig_fix_batch__sid", flat=True)
        a["lig1"] = lig
        a["lig1_con"] = all_spots.filter(raw_spot__lig_mob_batch__sid=lig).values_list(
            "raw_spot__lig_mob_batch__concentration").first()
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

