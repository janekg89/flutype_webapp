from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index_view, name='index'),
    url(r'^myexperiments/$', views.my_index_view, name='my_index'),
    url(r'^users/$', views.users_view, name='users'),
    url(r'^about/$', views.about_view, name='about'),

    url(r'^processes/$', views.processes_view, name='processesview'),
    url(r'^process/(?P<pk>[0-9]+)/$', views.process_view, name='processview'),

    url(r'^peptidebatches/$', views.peptide_batch_view, name='peptidebatches'),
    url(r'^peptidebatches_mobile/$', views.peptide_batch_mobile_view, name='peptidebatches_mobile'),
    url(r'^peptidebatches_fixed/$', views.peptide_batch_fixed_view, name='peptidebatches_fixed'),

    url(r'^peptides/$', views.peptide_view, name='peptides'),
    url(r'^peptides/new/$', views.peptide_new, name='peptide_new'),
    url(r'^peptides/edit/(?P<pk>[0-9]+)/$', views.peptide_edit, name='peptide_edit'),
    url(r'^peptides/delete/(?P<pk>[0-9]+)/$', views.peptide_delete,name='peptide_delete' ),

    url(r'^peptides_mobile/$', views.peptide_mobile_view, name='peptides_mobile'),
    url(r'^peptides_fixed/$', views.peptide_fixed_view, name='peptides_fixed'),

    url(r'^virusbatches/$', views.virus_batch_view, name='virusbatches'),
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
    url(r'^antibodybatches_mobile/$', views.antibody_batch_mobile_view, name='antibodybatches_mobile'),
    url(r'^antibodybatches_fixed/$', views.antibody_batch_fixed_view, name='antibodybatches_fixed'),

    url(r'^test/$', views.test_view, name='test'),
    url(r'^password/$', views.change_password_view, name='change_password'),

    # renders spot collections
    url(r'^rawspotcollection/(?P<pk>[0-9]+)/$', views.raw_spot_collection, name='rawspotcollectionview'),
    url(r'^qspotcollection/(?P<pk>[0-9]+)/$', views.quantified_spot_collection, name='qspotcollectionview'),

    # render heatmap image
    url(r'^qspotcollection/(?P<pk>[0-9]+)/data$', views.barplot_data_view, name='barplot_plotly'),
    url(r'^qspotcollection/(?P<pk>[0-9]+)/barplot_p$', views.highcharts_view, name='heatmap_highchart'),
    ]



