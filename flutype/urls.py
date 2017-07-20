from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    # url(r'^rawspotcollection/(?P<pk>[0-9]+)/$', views.RawSpotCollectionView.as_view(), name='rawspotcollectionview'),
    url(r'^rawspotcollection/(?P<pk>[0-9]+)/$', views.test_view, name='rawspotcollectionview'),
    url(r'^rawspotcollection/(?P<pk>[0-9]+)/heatmap$', views.heatmap_view, name='heatmapview'),
    url(r'^spotcollection/(?P<pk>[0-9]+)/$', views.SpotCollectionView.as_view(), name='spotcollectionview'),
    #url(r'^rawspotcollection/pepmap/$', views.RawSpotCollectionView.pepmap(), name='pepmap'),

]
