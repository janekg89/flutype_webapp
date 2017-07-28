from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index_view, name='index'),
    url(r'^users/$', views.users_view, name='users'),
    url(r'^about/$', views.about_view, name='about'),
    url(r'^peptidebatches/$', views.peptide_batch_view, name='peptidebatches'),
    url(r'^peptides/$', views.peptide_view, name='peptides'),
    url(r'^virusbatches/$', views.virus_batch_view, name='virusbatches'),
    url(r'^viruses/$', views.virus_view, name='viruses'),

    # renders spot collections
    url(r'^rawspotcollection/(?P<pk>[0-9]+)/$', views.raw_spot_collection, name='rawspotcollectionview'),
    url(r'^qspotcollection/(?P<pk>[0-9]+)/$', views.quantified_spot_collection, name='qspotcollectionview'),

    # render heatmap image
    url(r'^rawspotcollection/(?P<pk>[0-9]+)/heatmap$', views.desciptmap_view, name='desciptmapview'),
    url(r'^qspotcollection/(?P<pk>[0-9]+)/heatmap$', views.heatmap_view, name='heatmapview'),
    url(r'^qspotcollection/(?P<pk>[0-9]+)/barplot$', views.barplot_view, name='barplotview'),
    ]
