# -*- coding: utf-8 -*-

from django.db import models

class Area(models.Model):
    number = models.IntegerField(u'Номер участка', unique = True, error_messages = {
        'unique': u'Участок с таким номером уже есть'
    })
    address = models.CharField(u'Адрес', max_length = 256)

    x = models.FloatField(default = 43.95)
    y = models.FloatField(default = 56.30)
    zoom = models.IntegerField(default = 10)

    marks = models.CharField(max_length = 2048, blank = True)
