# -*- coding: utf-8 -*-

from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login, logout
from django.conf import settings
from django.utils.http import is_safe_url
from django.core.exceptions import PermissionDenied


from jwter.utils import render_to
from jwter.utils import UpdateViewExtPerms

from jwter.areas.models import Area, Folder, ArchivedArea
from jwter.areas.forms  import AreaForm, ArchivedAreaForm, LoginForm
from jwter.areas.printer import print_many_areas
from jwter.areas.mixins import SmartListMixin
from jwter.areas.decorators import class_decorator


@login_required
def index(request):
    return redirect(Folder.get_inbox())


@class_decorator(login_required)
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


@class_decorator(permission_required('areas.can_view_archive'))
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



@class_decorator(login_required)
class AreaEdit(UpdateViewExtPerms):
    model = Area
    form_class = AreaForm
    template_name = 'areas/edit.html'

    save_permission = 'areas.change_area'

    def get_object(self):
        return get_object_or_404(Area, folder_id = self.kwargs['folder_id'], number = self.kwargs['number'])

    def get_context_data(self, **kwargs):
        context = super(AreaEdit, self).get_context_data(**kwargs)
        context['folder'] = self.get_object().folder
        return context

    def get_success_url(self):
        if 'apply' in self.request.REQUEST:
            return self.object.get_absolute_url()
        else:
            return self.object.folder.get_absolute_url()


@class_decorator(permission_required('areas.change_archivedarea'))
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

    def form_valid(self, form):
        if self.request.REQUEST.get('restore_to', '') and not self.request.user.has_perm('areas.can_restore'):
            raise PermissionDenied()
        return super(ArchivedAreaEdit, self).form_valid(form)

    def get_success_url(self):
        if 'apply' in self.request.REQUEST:
            return self.get_object().get_absolute_url()
        else:
            return reverse('archive')




@class_decorator(permission_required('areas.add_area'))
class AreaNew(CreateView):
    model = Area
    form_class = AreaForm
    template_name = 'areas/edit.html'

    def get_folder(self):
        return get_object_or_404(Folder, pk = self.kwargs['folder_id'])

    def get_initial(self):
        initial = super(AreaNew, self).get_initial()
        folder = self.get_folder()
        initial['folder'] = folder
        initial['number'] = Area.first_free_number(folder)
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



@class_decorator(login_required)
class AreaPrint(SingleObjectMixin, View):
    model = Area

    def get_object(self):
        return get_object_or_404(Area, folder_id = self.kwargs['folder_id'], number = self.kwargs['number'])

    def get(self, request, *args, **kwargs):
        # pdf = print_one_area(self.get_object())
        pdf = print_many_areas([ self.get_object() ])
        return HttpResponse(pdf, 'application/pdf')


@class_decorator(permission_required('areas.can_archive'))
class AreaArchive(SingleObjectMixin, View):
    model = Area

    def get_object(self):
        return get_object_or_404(Area, folder_id = self.kwargs['folder_id'], number = self.kwargs['number'])

    def post(self, request, *args, **kwargs):
        area = self.get_object()
        folder = area.folder
        area.archive()
        return redirect(folder)


@class_decorator(login_required)
class FolderPrint(SingleObjectMixin, View):
    model = Folder

    def get(self, request, *args, **kwargs):
        pdf = print_many_areas(self.get_object().area_set.all())
        return HttpResponse(pdf, 'application/pdf')


@class_decorator(login_required)
class FolderList(ListView):
    template_name = 'folders/list.html'

    model = Folder

    def get_context_data(self, **kwargs):
        context = super(FolderList, self).get_context_data(**kwargs)
        context['all_folders'] = Folder.objects.all()
        context['folder_settings'] = True
        return context


@class_decorator(login_required)
class FolderEdit(UpdateViewExtPerms):
    model = Folder
    template_name = 'folders/edit.html'
    save_permission = 'areas.change_folder'
    success_url = reverse_lazy('folders')


@class_decorator(permission_required('areas.change_folder'))
class FolderRename(SingleObjectMixin, View):
    model = Folder

    def post(self, request, *args, **kwargs):
        f = self.get_object()
        f.name = request.REQUEST['new_name']
        f.save()
        return redirect('folders')

@class_decorator(permission_required('areas.add_folder'))
class FolderNew(CreateView):
    model = Folder
    template_name = 'folders/edit.html'

    # def form_valid(self, *args, **kwargs):
    #     Folder(name = request.REQUEST['name']).save()
    #     return redirect('folders')

@class_decorator(permission_required('areas.delete_folder'))
class FolderDelete(SingleObjectMixin, View):
    model = Folder

    def post(self, request, *args, **kwargs):
        f = self.get_object()
        for area in f.area_set.all():
            area.archive()
        f.delete()
        return redirect('folders')



@class_decorator(permission_required('areas.can_move_all'))
class MoveAll(View):

    def post(self, request, *args, **kwargs):
        _from = get_object_or_404(Folder, pk = int(request.REQUEST['from']))
        _to   = get_object_or_404(Folder, pk = int(request.REQUEST['to']))

        try:
            Area.objects.filter(folder = _from).update(folder = _to)
            return redirect(_to)
        except IntegrityError:
            messages.error(self.request, u'В группах есть участки с одинаковыми номерами')
            return redirect(_from)


@class_decorator(permission_required('areas.change_area'))
class AreaMove(SingleObjectMixin, View):
    model = Area

    def get_object(self):
        return get_object_or_404(Area, folder_id = self.kwargs['folder_id'], number = self.kwargs['number'])

    def post(self, request, *args, **kwargs):
        area = self.get_object()
        folder = get_object_or_404(Folder, pk = int(request.REQUEST['to']))
        area.folder = folder

        try:
            area.save()
        except IntegrityError:
            messages.error(self.request, u'В группе {} уже есть участок с таким номером'.format(folder.name))

        return redirect(get_object_or_404(Folder, pk = int(request.REQUEST['back_to'])))



@class_decorator(permission_required('areas.can_restore'))
class ArchiveRestore(SingleObjectMixin, View):
    model = ArchivedArea

    def post(self, request, *args, **kwargs):
        aarea = self.get_object()

        try:
            aarea.restore_to(get_object_or_404(Folder, pk = int(request.REQUEST['to'])))
        except IntegrityError:
            messages.error(self.request, u'Участок с таким номером уже существует')

        return redirect('archive')



class Login(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def get_redirect_url(self):
        next = self.request.REQUEST.get('next', '')

        if not is_safe_url(url = next, host = self.request.get_host()):
            next = settings.LOGIN_REDIRECT_URL

        return next


    # def get(self, request, *args, **kwargs):
    #     if request.user.is_authenticated():
    #         return redirect(self.get_redirect_url())

    #     return super(Login, self).get(request, *args, **kwargs)

    def form_valid(self, form):

        login(self.request, form.get_user())

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return redirect(self.get_redirect_url())


class Logout(View):

    def get(self, request, *args, **kwargs):
        logout(request)

        return redirect('login')
