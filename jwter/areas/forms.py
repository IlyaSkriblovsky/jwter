# -*- coding: utf-8 -*-

from django import forms

from jwter.areas.models import Area
from jwter.utils import ExtendedMetaModelForm


class AreaForm(ExtendedMetaModelForm):
    class Meta:
        model = Area

        field_args = {
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
