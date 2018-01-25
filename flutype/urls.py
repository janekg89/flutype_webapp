from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import url, include


from . import views

urlpatterns = [
    url(r'^$', views.studies_view, name='index'),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^mystudies/$', views.my_studies_view, name='my_studies'),
    url(r'^uploadfile_study/(?P<sid>.*)/$', views.upload_file_study, name='upload_file_study'),
    url(r'^study/(?P<sid>.*)/$', views.study_view, name='study'),
    url(r'^study/(?P<sid>.*)/import_measurement$', views.import_measurement_view, name='import_measurement'),
    url(r'^studies/new/$', views.study_new, name='study_new'),
    url(r'^study_ligands/(?P<sid>.*)/$', views.study_ligands_view, name='study_ligands'),

    url(r'^tutorial_db/$', views.tutorial_db_view, name='tutorial_db'),
    url(r'^glossary/$', views.glossary_view, name='glossary'),

    url(r'^measurements/$', views.measurements_view, name='measurements'),
    url(r'^mymeasurements/$', views.my_measurements_view, name='my_measurements'),
    url(r'^measurement/(?P<sid>.*)/$',views.measurement_view, name='rawspotcollectionview'),
    url(r'^measurement_ligands/(?P<sid>.*)/$', views.measurement_ligands_view, name='measurement_ligands'),
    url(r'^m/(?P<measurement_sid>.*)/result/(?P<sid>.*)/$', views.measurement_result_view, name='qspotcollectionview'),
    url(r'^m/(?P<measurement_sid>.*)/result/(?P<sid>.*)/data$', views.barplot_data_view, name='barplot_plotly1'),
    url(r'^m/(?P<measurement_sid>.*)/result/(?P<sid>.*)/barplot_p$', views.highcharts_view, name='heatmap_highchart1'),
    url(r'^uploadfile_measurement/(?P<sid>.*)/$', views.upload_file_measurement, name='upload_file_measurement'),

    url(r'^users/$', views.users_view, name='users'),
    url(r'^about/$', views.about_en_view, name='about'),
    url(r'^about_de/$', views.about_de_view, name='about_de'),

    url(r'^database_scheme/$', views.database_scheme_en_view, name='database_scheme'),
    url(r'^database_scheme_de/$', views.database_scheme_de_view, name='database_scheme_de'),

    url(r'^gal_file/$', views.gal_file_view, name='gal_file'),
    url(r'^raw_gal_file/$', views.raw_gal_file_view, name='raw_gal_file'),
    url(r'^tutorial/$', views.tutorial_en_view, name='tutorial'),
    url(r'^tree/$', views.tutorial_tree_view, name='tutorial_tree'),
    url(r'^tutorial_de/$', views.tutorial_de_view, name='tutorial_de'),

    url(r'^steps/$', views.steps_view, name='steps'),

    url(r'^processes/$', views.processes_view, name='processes'),
    url(r'^process/(?P<sid>.*)/$', views.process_view, name='processview'),
    url(r'^image/processtep/(?P<id>.*)/$', views.image_process_view, name='imageviewprocess'),

    url(r'^g/(?P<model_name>.*)/new/$', views.new_view, name='new'),
    url(r'^ligandbatch/(?P<model_name>.*)/new/$', views.ligandbatch_new, name='new_ligandbatch'),
    url(r'^studies/new/$', views.study_new, name='study_new'),

    url(r'^g/(?P<model_name>.*)/(?P<sid>.*)/delete$', views.delete_view, name='delete'),
    url(r'^g/(?P<model_name>.*)/(?P<sid>.*)/edit$', views.edit_view, name='edit'),



    url(r'^buffers/$', views.buffer_view, name='buffers'),
    url(r'^peptides/$', views.peptide_view, name='peptides'),
    url(r'^complexes/$', views.complex_view, name='complexes'),
    url(r'^viruses/$', views.virus_view, name='viruses'),
    url(r'^antibodies/$', views.antibody_view, name='antibodies'),

    url(r'^bufferbatches/$', views.buffer_batch_view, name='bufferbatches'),
    url(r'^peptidebatches/$', views.peptide_batch_view, name='peptidebatches'),
    url(r'^complexbatches/$', views.complex_batch_view, name='complexbatches'),
    url(r'^virusbatches/$', views.virus_batch_view, name='virusbatches'),
    url(r'^antibodybatches/$', views.antibody_batch_view, name='antibodybatches'),

    url(r'^password/$', views.change_password_view, name='change_password'),

    url(r'^qspotcollection/(?P<sid>.*)/data$', views.barplot_data_view, name='barplot_plotly'),
    url(r'^qspotcollection/(?P<sid>.*)/barplot_p$', views.highcharts_view, name='heatmap_highchart'),
]