from django.conf.urls import patterns, url

from jwter.areas.views import *

urlpatterns = patterns('jwter.areas.views',
    url(r'^$', index, name = 'index'),

    url(r'^login$', Login.as_view(), name = 'login'),
    url(r'^logout$', Logout.as_view(), name = 'logout'),

    url(r'^folders$', FolderList.as_view(), name = 'folders'),

    url(r'^archive$', Archive.as_view(), name = 'archive'),
    url(r'^archive/(?P<pk>\d+)$', ArchivedAreaEdit.as_view(), name = 'archive-edit'),
    url(r'^archive/(?P<pk>\d+)/restore$', ArchiveRestore.as_view(), name = 'archive-restore'),

    url(r'^folder/new$', FolderNew.as_view(), name = 'folder-new'),
    url(r'^folder/(?P<pk>\d+)$', FolderView.as_view(), name = 'folder'),
    url(r'^folder/(?P<folder_id>\d+)/new$', AreaNew.as_view(), name = 'area-new'),
    url(r'^folder/(?P<pk>\d+)/print$', FolderPrint.as_view(), name = 'folder-print'),
    url(r'^folder/(?P<pk>\d+)/rename', FolderRename.as_view(), name = 'folder-rename'),
    url(r'^folder/(?P<pk>\d+)/delete', FolderDelete.as_view(), name = 'folder-delete'),
    url(r'^folder/(?P<pk>\d+)/edit', FolderEdit.as_view(), name = 'folder-edit'),

    url(r'^area/(?P<folder_id>\d+)/(?P<number>\d+)$', AreaEdit.as_view(), name = 'area-edit'),
    url(r'^area/(?P<folder_id>\d+)/(?P<number>\d+)/print$', AreaPrint.as_view(), name = 'area-print'),
    url(r'^area/(?P<folder_id>\d+)/(?P<number>\d+)/archive$', AreaArchive.as_view(), name = 'area-archive'),
    url(r'^area/(?P<folder_id>\d+)/(?P<number>\d+)/move$', AreaMove.as_view(),    name = 'area-move'),
    url(r'^move-all$', MoveAll.as_view(), name = 'area-move-all'),
)
