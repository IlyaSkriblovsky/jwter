# -*- coding: utf-8 -*-

import hashlib

from django.db import models
from django.core.files.base import ContentFile


class Area(models.Model):
    number = models.IntegerField(u'Номер участка', unique = True, error_messages = {
        'unique': u'Участок с таким номером уже есть'
    })
    address = models.CharField(u'Адрес', max_length = 256)

    x = models.FloatField(default = 43.95)
    y = models.FloatField(default = 56.30)
    zoom = models.IntegerField(default = 10)

    marks = models.CharField(max_length = 2048, blank = True)



class MapCache(models.Model):
    urlhash = models.CharField(max_length = 40, unique = True)
    url = models.CharField(max_length = 2048)

    map = models.FileField(upload_to = 'mapcache')


    @staticmethod
    def save_map(url, content):
        urlhash = hashlib.sha1(url).hexdigest()
        mc = MapCache(urlhash = urlhash, url = url)
        mc.map.save(urlhash, ContentFile(content))
        mc.save()
        return mc


    @staticmethod
    def get_map(url):
        urlhash = hashlib.sha1(url).hexdigest()
        try:
            mc = MapCache.objects.get(urlhash = urlhash, url = url)
            return mc.map.read()
        except MapCache.DoesNotExist:
            return None
