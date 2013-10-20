# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import AuthenticationForm

from jwter.areas.models import Area, ArchivedArea, Folder
from jwter.utils import ExtendedMetaModelForm


_area_fields_spec = {
    'number': {
        '+error_messages': {
            'required': u'Укажите номер участка',
            'invalid':  u'Номер участка должен быть числом',
            'unique':   u'Участок с таким номером уже есть',
        }
    },

    'address': {
        '+error_messages': {
            'required': u'Укажите адрес',
        }
    },

    'x': {
        'widget': forms.HiddenInput()
    },

    'y': {
        'widget': forms.HiddenInput()
    },

    'zoom': {
        'widget': forms.HiddenInput()
    },

    'marks': {
        'widget': forms.HiddenInput()
    }
}


class AreaForm(ExtendedMetaModelForm):
    class Meta:
        model = Area

        field_args = _area_fields_spec


class ArchivedAreaForm(ExtendedMetaModelForm):
    class Meta:
        model = ArchivedArea

        field_args = _area_fields_spec


    restore_to = forms.CharField(widget = forms.HiddenInput(), required = False)


    def clean(self):
        if self.cleaned_data.get('restore_to', ''):
            if Area.objects.filter(number = self.cleaned_data['number']):
                raise ValidationError(u'Участок с таким номером уже существует')

        return super(ArchivedAreaForm, self).clean()

    def save(self):
        aarea = super(ArchivedAreaForm, self).save()
        if self.cleaned_data.get('restore_to', ''):
            aarea.restore_to(get_object_or_404(Folder, id = int(self.cleaned_data['restore_to'])))



class LoginForm(AuthenticationForm):
    username = forms.CharField(label = u'Логин', max_length = 30, error_messages = {
        'required': u'Это поле обязательно'
    })
    password = forms.CharField(label = u'Пароль', widget = forms.PasswordInput, error_messages = {
        'required': u'Это поле обязательно'
    })

    error_messages = {
        'invalid_login': u'Неправильный логин и/или пароль',
        'no_cookies': u'В вашем браузере отключены куки. Они обязательны для входа',
        'inactive': u'Эта учётная запись неактивна',
    }
