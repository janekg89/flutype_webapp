from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index_view, name='index'),
    url(r'^myexperiments/$', views.my_index_view, name='my_index'),
    url(r'^users/$', views.users_view, name='users'),
    url(r'^about/$', views.about_view, name='about'),
    url(r'^peptidebatches/$', views.peptide_batch_view, name='peptidebatches'),
    url(r'^peptidebatches_mobile/$', views.peptide_batch_mobile_view, name='peptidebatches_mobile'),
    url(r'^peptidebatches_fixed/$', views.peptide_batch_fixed_view, name='peptidebatches_fixed'),

    url(r'^peptides/$', views.peptide_view, name='peptides'),
    url(r'^peptides_mobile/$', views.peptide_mobile_view, name='peptides_mobile'),
    url(r'^peptides_fixed/$', views.peptide_fixed_view, name='peptides_fixed'),

    url(r'^virusbatches/$', views.virus_batch_view, name='virusbatches'),
    url(r'^virusbatches_mobile/$', views.virus_batch_mobile_view, name='virusbatches_mobile'),
    url(r'^virusbatches_fixed/$', views.virus_batch_fixed_view, name='virusbatches_fixed'),

    url(r'^viruses/$', views.virus_view, name='viruses'),
    url(r'^viruses_mobile/$', views.virus_mobile_view, name='viruses_mobile'),
    url(r'^viruses_fixed/$', views.virus_fixed_view, name='viruses_fixed'),

    url(r'^test/$', views.test_view, name='test'),
    url(r'^password/$', views.change_password_view, name='change_password'),

    # renders spot collections
    url(r'^rawspotcollection/(?P<pk>[0-9]+)/$', views.raw_spot_collection, name='rawspotcollectionview'),
    url(r'^qspotcollection/(?P<pk>[0-9]+)/$', views.quantified_spot_collection, name='qspotcollectionview'),

    # render heatmap image
    url(r'^rawspotcollection/(?P<pk>[0-9]+)/heatmap$', views.desciptmap_view, name='desciptmapview'),
    url(r'^qspotcollection/(?P<pk>[0-9]+)/heatmap$', views.heatmap_view, name='heatmapview'),
    url(r'^qspotcollection/(?P<pk>[0-9]+)/barplot$', views.barplot_view, name='barplotview'),
    ]
