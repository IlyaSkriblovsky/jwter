# -*- coding: utf-8 -*-

import hashlib

from django.db import models
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse_lazy


class Folder(models.Model):
    class Meta:
        ordering = ['-is_inbox', 'is_archive', 'name']

    name = models.CharField(u'Имя', max_length = 64)

    is_inbox   = models.BooleanField()
    is_archive = models.BooleanField()


    def __unicode__(self):
        return self.name or u'<папка>'

    def get_absolute_url(self):
        return reverse_lazy('folder', kwargs = { 'pk': self.id })

    @staticmethod
    def get_inbox():
        return Folder.objects.get(is_inbox = True)

    @staticmethod
    def get_archive():
        return Folder.objects.get(is_archive = True)


class Area(models.Model):
    folder = models.ForeignKey(Folder, verbose_name = u'Папка')

    number = models.IntegerField(u'Номер участка', unique = True, error_messages = {
        'unique': u'Участок с таким номером уже есть'
    })
    address = models.CharField(u'Адрес', max_length = 256)

    x = models.FloatField(default = 43.95)
    y = models.FloatField(default = 56.30)
    zoom = models.IntegerField(default = 10)

    marks = models.CharField(max_length = 2048, blank = True)

    def __unicode__(self):
        return u'[{0}] {1}'.format(self.number, self.address)

    def get_absolute_url(self):
        return reverse_lazy('area-edit', kwargs = { 'pk': self.id })



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
