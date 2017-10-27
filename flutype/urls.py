from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.studies_view, name='index'),
    url(r'^mystudies/$', views.my_studies_view, name='my_studies'),
    url(r'^uploadfile_study/(?P<pk>[0-9]+)/$', views.upload_file_study, name='upload_file_study'),

    url(r'^study/(?P<pk>[0-9]+)/$', views.study_view, name='study'),
    url(r'^study_ligands/(?P<pk>[0-9]+)/$', views.study_ligands_view, name='study_ligands'),

    url(r'^tutorial_db/$', views.tutorial_db_view, name='tutorial_db'),

    url(r'^measurements/$', views.measurements_view, name='measurements'),
    url(r'^mymeasurements/$', views.my_measurements_view, name='my_measurements'),

    url(r'^measurement/(?P<pk>[0-9]+)/$',views.measurement_view, name='rawspotcollectionview'),
    url(r'^measurement_ligands/(?P<pk>[0-9]+)/$', views.measurement_ligands_view, name='measurement_ligands'),
    url(r'^measurement_result/(?P<pk>[0-9]+)/$', views.measurement_result_view, name='qspotcollectionview'),
    url(r'^measurement_result/(?P<pk>[0-9]+)/data$', views.barplot_data_view, name='barplot_plotly1'),
    url(r'^measurement_result/(?P<pk>[0-9]+)/barplot_p$', views.highcharts_view, name='heatmap_highchart1'),

    url(r'^uploadfile_measurement/(?P<pk>[0-9]+)/$', views.upload_file_measurement, name='upload_file_measurement'),

    url(r'^users/$', views.users_view, name='users'),
    url(r'^about/$', views.about_en_view, name='about'),
    url(r'^about_de/$', views.about_de_view, name='about_de'),

    url(r'^database_scheme/$', views.database_scheme_en_view, name='database_scheme'),
    url(r'^database_scheme_de/$', views.database_scheme_de_view, name='database_scheme_de'),

    url(r'^gal_file/$', views.gal_file_view, name='gal_file'),

    url(r'^tutorial/$', views.tutorial_en_view, name='tutorial'),
    url(r'^tree/$', views.tutorial_tree_view, name='tutorial_tree'),

    url(r'^tutorial_de/$', views.tutorial_de_view, name='tutorial_de'),

    url(r'^steps/$', views.steps_view, name='steps'),
    url(r'^steps/new/(?P<class_name>\w+)/$', views.step_new, name='step_new'),
    url(r'^steps/edit/(?P<pk>[0-9]+)/$', views.step_edit, name='step_edit'),
    url(r'^steps/delete/(?P<pk>[0-9]+)/$', views.step_delete, name='step_delete'),

    url(r'^processes/$', views.processes_view, name='processes'),

    url(r'^process/(?P<pk>[0-9]+)/$', views.process_view, name='processview'),

    url(r'^image/(?P<pk>[0-9]+)/$', views.image_view, name='imageview'),
    url(r'^image/process/(?P<pk>[0-9]+)/$', views.image_process_view, name='imageviewprocess'),

    url(r'^peptidebatches/$', views.peptide_batch_view, name='peptidebatches'),
    url(r'^peptidebatches/new/$', views.peptide_batch_new, name='peptide_batch_new'),
    url(r'^peptidebatches/edit/(?P<pk>[0-9]+)/$', views.peptide_batch_edit, name='peptide_batch_edit'),
    url(r'^peptidebatches/delete/(?P<pk>[0-9]+)/$', views.peptide_batch_delete, name='peptide_batch_delete'),

    url(r'^peptidebatches_mobile/$', views.peptide_batch_mobile_view, name='peptidebatches_mobile'),
    url(r'^peptidebatches_fixed/$', views.peptide_batch_fixed_view, name='peptidebatches_fixed'),

    url(r'^peptides/$', views.peptide_view, name='peptides'),
    url(r'^peptides/new/$', views.peptide_new, name='peptide_new'),
    url(r'^peptides/edit/(?P<pk>[0-9]+)/$', views.peptide_edit, name='peptide_edit'),
    url(r'^peptides/delete/(?P<pk>[0-9]+)/$', views.peptide_delete, name='peptide_delete'),

    url(r'^peptides_mobile/$', views.peptide_mobile_view, name='peptides_mobile'),
    url(r'^peptides_fixed/$', views.peptide_fixed_view, name='peptides_fixed'),

    url(r'^complexes/$', views.complex_view, name='complexes'),
    url(r'^complexes/new/$', views.complex_new, name='complex_new'),
    url(r'^complexes/edit/(?P<pk>[0-9]+)/$', views.complex_edit, name='complex_edit'),
    url(r'^complexes/delete/(?P<pk>[0-9]+)/$', views.complex_delete, name='complex_delete'),

    url(r'^complexes_mobile/$', views.complex_mobile_view, name='complexes_mobile'),
    url(r'^complexes_fixed/$', views.complex_fixed_view, name='complexes_fixed'),

    url(r'^complexbatches/$', views.complex_batch_view, name='complexbatches'),
    url(r'^complexbatches/new/$', views.complex_batch_new, name='complex_batch_new'),
    url(r'^complexbatches/edit/(?P<pk>[0-9]+)/$', views.complex_batch_edit, name='complex_batch_edit'),
    url(r'^complexbatches/delete/(?P<pk>[0-9]+)/$', views.complex_batch_delete, name='complex_batch_delete'),

    url(r'^complexbatches_mobile/$', views.complex_batch_mobile_view, name='complexbatches_mobile'),
    url(r'^complexbatches_fixed/$', views.complex_batch_fixed_view, name='complexbatches_fixed'),


    url(r'^virusbatches/$', views.virus_batch_view, name='virusbatches'),
    url(r'^virusbatches/new/$', views.virus_batch_new, name='virus_batch_new'),
    url(r'^virusbatches/edit/(?P<pk>[0-9]+)/$', views.virus_batch_edit, name='virus_batch_edit'),
    url(r'^virusbatches/delete/(?P<pk>[0-9]+)/$', views.virus_batch_delete, name='virus_batch_delete'),

    url(r'^virusbatches_mobile/$', views.virus_batch_mobile_view, name='virusbatches_mobile'),
    url(r'^virusbatches_fixed/$', views.virus_batch_fixed_view, name='virusbatches_fixed'),

    url(r'^viruses/$', views.virus_view, name='viruses'),
    url(r'^viruses/new/$', views.virus_new, name='virus_new'),
    url(r'^viruses/edit/(?P<pk>[0-9]+)/$', views.virus_edit, name='virus_edit'),
    url(r'^viruses/delete/(?P<pk>[0-9]+)/$', views.virus_delete, name='virus_delete'),

    url(r'^viruses_mobile/$', views.virus_mobile_view, name='viruses_mobile'),
    url(r'^viruses_fixed/$', views.virus_fixed_view, name='viruses_fixed'),

    url(r'^antibodies/$', views.antibody_view, name='antibodies'),
    url(r'^antibodies/new/$', views.antibody_new, name='antibody_new'),
    url(r'^antibodies/edit/(?P<pk>[0-9]+)/$', views.antibody_edit, name='antibody_edit'),
    url(r'^antibodies/delete/(?P<pk>[0-9]+)/$', views.antibody_delete, name='antibody_delete'),

    url(r'^antibodies_mobile/$', views.antibody_mobile_view, name='antibodies_mobile'),
    url(r'^antibodies_fixed/$', views.antibody_fixed_view, name='antibodies_fixed'),

    url(r'^antibodybatches/$', views.antibody_batch_view, name='antibodybatches'),
    url(r'^antibodybatches/new/$', views.antibody_batch_new, name='antibody_batch_new'),
    url(r'^antibodybatches/edit/(?P<pk>[0-9]+)/$', views.antibody_batch_edit, name='antibody_batch_edit'),
    url(r'^antibodybatches/delete/(?P<pk>[0-9]+)/$', views.antibody_batch_delete, name='antibody_batch_delete'),

    url(r'^antibodybatches_mobile/$', views.antibody_batch_mobile_view, name='antibodybatches_mobile'),
    url(r'^antibodybatches_fixed/$', views.antibody_batch_fixed_view, name='antibodybatches_fixed'),

    url(r'^password/$', views.change_password_view, name='change_password'),


    url(r'^qspotcollection/(?P<pk>[0-9]+)/data$', views.barplot_data_view, name='barplot_plotly'),
    url(r'^qspotcollection/(?P<pk>[0-9]+)/barplot_p$', views.highcharts_view, name='heatmap_highchart'),
]
