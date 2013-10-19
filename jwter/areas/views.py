# -*- coding: utf-8 -*-

from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib import messages


from jwter.utils import render_to

from jwter.areas.models import Area, Folder, ArchivedArea
from jwter.areas.forms  import AreaForm, ArchivedAreaForm
from jwter.areas.printer import print_one_area, print_many_areas
from jwter.areas.mixins import SmartListMixin


# @render_to('areas/list.html')
# def area_list(request):
#     return {
#         'areas': Area.objects.all(),
#     }


def index(request):
    return redirect(Folder.get_inbox())


class FolderView(SmartListMixin, ListView):
    template_name = 'areas/list.html'

    model = Area
    list_fields = ('number', 'address')
    paginate_by = 15

    _folder = None

    def get_folder(self):
        if not self._folder:
            self._folder = get_object_or_404(Folder, pk = self.kwargs['pk'])
        return self._folder

    def get_queryset(self):
        folder = self.get_folder()
        return super(FolderView, self).get_queryset().filter(folder = folder)

    def get_context_data(self, **kwargs):
        context = super(FolderView, self).get_context_data(**kwargs)
        context['folder'] = self.get_folder()
        context['all_folders'] = Folder.objects.all()
        return context


class Archive(SmartListMixin, ListView):
    template_name = 'areas/archive.html'

    model = ArchivedArea
    list_fields = ('number', 'address')
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(Archive, self).get_context_data(**kwargs)
        context['archive'] = True
        context['all_folders'] = Folder.objects.all()
        return context



class AreaList(SmartListMixin, ListView):
    template_name = 'areas/list.html'

    model = Area
    list_fields = ('number', 'address')

    paginate_by = 15


class AreaEdit(UpdateView):
    model = Area
    slug_field = 'number'
    slug_url_kwarg = 'number'
    form_class = AreaForm
    template_name = 'areas/edit.html'

    def get_context_data(self, **kwargs):
        context = super(AreaEdit, self).get_context_data(**kwargs)
        context['folder'] = self.get_object().folder
        return context

    def post(self, request, *args, **kwargs):
        # print '!!!', self.get_object().number
        return super(AreaEdit, self).post(request, *args, **kwargs)

    def get_success_url(self):
        if 'apply' in self.request.REQUEST:
            return self.object.get_absolute_url()
        else:
            return self.object.folder.get_absolute_url()


class ArchivedAreaEdit(UpdateView):
    model = ArchivedArea
    form_class = ArchivedAreaForm
    template_name = 'areas/edit.html'
    context_object_name = 'area'

    def get_context_data(self, **kwargs):
        context = super(ArchivedAreaEdit, self).get_context_data(**kwargs)
        context['archived'] = True
        context['all_folders'] = Folder.objects.all()
        return context

    def get_success_url(self):
        if 'apply' in self.request.REQUEST:
            return self.get_object().get_absolute_url()
        else:
            return reverse('archive')




class AreaNew(CreateView):
    model = Area
    form_class = AreaForm
    template_name = 'areas/edit.html'

    def get_folder(self):
        return get_object_or_404(Folder, pk = self.kwargs['folder_id'])

    def get_initial(self):
        initial = super(AreaNew, self).get_initial()
        initial['folder'] = self.get_folder()
        return initial

    def get_context_data(self, **kwargs):
        context = super(AreaNew, self).get_context_data(**kwargs)
        context['folder'] = self.get_folder()
        return context

    def get_success_url(self):
        if 'apply' in self.request.REQUEST:
            return self.object.get_absolute_url()
        else:
            return self.object.folder.get_absolute_url()


# class AreaDelete(SingleObjectMixin, View):
#     model = Area
#     slug_field = 'number'
#     slug_url_kwarg = 'number'
# 
#     def post(self, request, *args, **kwargs):
#         folder = self.get_object().folder
#         self.get_object().delete()
#         return redirect(folder)



class AreaPrint(SingleObjectMixin, View):
    model = Area
    slug_field = 'number'
    slug_url_kwarg = 'number'

    def get(self, request, *args, **kwargs):
        # pdf = print_one_area(self.get_object())
        pdf = print_many_areas([ self.get_object() ])
        return HttpResponse(pdf, 'application/pdf')


class AreaArchive(SingleObjectMixin, View):
    model = Area
    slug_field = 'number'
    slug_url_kwarg = 'number'

    def post(self, request, *args, **kwargs):
        area = self.get_object()
        folder = area.folder
        area.archive()
        return redirect(folder)


# class PrintAllAreas(View):
# 
#     def get(self, request):
#         pdf = print_many_areas(Area.objects.all())
#         return HttpResponse(pdf, 'application/pdf')


class FolderPrint(SingleObjectMixin, View):
    model = Folder

    def get(self, request, *args, **kwargs):
        pdf = print_many_areas(self.get_object().area_set.all())
        return HttpResponse(pdf, 'application/pdf')


class FolderList(ListView):
    template_name = 'folders/list.html'

    model = Folder

    def get_context_data(self, **kwargs):
        context = super(FolderList, self).get_context_data(**kwargs)
        context['all_folders'] = Folder.objects.all()
        context['folder_settings'] = True
        return context


class FolderRename(SingleObjectMixin, View):
    model = Folder

    def post(self, request, *args, **kwargs):
        f = self.get_object()
        f.name = request.REQUEST['new_name']
        f.save()
        return HttpResponse('ok')

class FolderNew(View):
    def post(self, request, *args, **kwargs):
        Folder(name = request.REQUEST['name']).save()
        return redirect('folders')

class FolderDelete(SingleObjectMixin, View):
    model = Folder

    def post(self, request, *args, **kwargs):
        f = self.get_object()
        for area in f.area_set.all():
            area.archive()
        f.delete()
        return redirect('folders')



class MoveAll(View):

    def post(self, request, *args, **kwargs):
        _from = get_object_or_404(Folder, pk = int(request.REQUEST['from']))
        _to   = get_object_or_404(Folder, pk = int(request.REQUEST['to']))

        Area.objects.filter(folder = _from).update(folder = _to)

        return redirect(_to)


class Move(SingleObjectMixin, View):
    model = Area
    slug_field = 'number'
    slug_url_kwarg = 'number'

    def post(self, request, *args, **kwargs):
        area = self.get_object()
        area.folder = get_object_or_404(Folder, pk = int(request.REQUEST['to']))
        area.save()

        return redirect(get_object_or_404(Folder, pk = int(request.REQUEST['back_to'])))



class ArchiveRestore(SingleObjectMixin, View):
    model = ArchivedArea

    def post(self, request, *args, **kwargs):
        aarea = self.get_object()

        try:
            aarea.restore_to(get_object_or_404(Folder, pk = int(request.REQUEST['to'])))
        except IntegrityError:
            messages.error(self.request, u'Участок с таким номером уже существует')

        return redirect('archive')
