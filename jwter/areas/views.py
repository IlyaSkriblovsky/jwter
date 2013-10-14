from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect
from django.http import HttpResponse


from jwter.utils import render_to

from jwter.areas.models import Area
from jwter.areas.forms  import AreaForm
from jwter.areas.printer import print_one_area, print_many_areas


# @render_to('areas/list.html')
# def area_list(request):
#     return {
#         'areas': Area.objects.all(),
#     }


class AreaList(ListView):
    model = Area
    template_name = 'areas/list.html'


class AreaEdit(UpdateView):
    model = Area
    form_class = AreaForm
    template_name = 'areas/edit.html'
    # success_url = reverse_lazy('area-list')

    def get_success_url(self):
        if 'apply' in self.request.REQUEST:
            return reverse('area-edit', kwargs = { 'pk': self.get_object().id })
        else:
            return reverse('area-list')


class AreaNew(CreateView):
    model = Area
    form_class = AreaForm
    template_name = 'areas/edit.html'
    success_url = reverse_lazy('area-list')


class AreaDelete(SingleObjectMixin, View):
    model = Area

    def post(self, request, *args, **kwargs):
        self.get_object().delete()
        return redirect('area-list')



class AreaPrint(SingleObjectMixin, View):
    model = Area

    def get(self, request, *args, **kwargs):
        pdf = print_one_area(self.get_object())
        return HttpResponse(pdf, 'application/pdf')


class PrintAllAreas(View):

    def get(self, request):
        pdf = print_many_areas(Area.objects.all())
        return HttpResponse(pdf, 'application/pdf')
