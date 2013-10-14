from django.conf.urls import patterns, include, url

from jwter.areas.views import *

urlpatterns = patterns('jwter.areas.views',
    url(r'^$', AreaList.as_view(), name = 'area-list'),
    url(r'^area/(?P<pk>\d+)$', AreaEdit.as_view(), name = 'area-edit'),
    url(r'^area/new$', AreaNew.as_view(), name = 'area-new'),
    url(r'^area/(?P<pk>\d+)/delete$', AreaDelete.as_view(), name = 'area-delete'),
    url(r'^area/(?P<pk>\d+)/print$', AreaPrint.as_view(), name = 'area-print'),
    url(r'^area/print-all$', PrintAllAreas.as_view(), name = 'area-print-all'),
)
