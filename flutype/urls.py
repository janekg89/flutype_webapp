from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index_view, name='index'),
    url(r'^peptidebatches/$', views.peptide_batch_view, name='peptidebatches'),

    url(r'^rawspotcollection/(?P<pk>[0-9]+)/$', views.raw_spot_collection_detail_view, name='rawspotcollectionview'),

    # render heatmap image
    url(r'^rawspotcollection/(?P<pk>[0-9]+)/heatmap$', views.heatmap_view, name='heatmapview'),
    url(r'^spotcollection/(?P<pk>[0-9]+)/$', views.SpotCollectionView.as_view(), name='spotcollectionview'),


]
