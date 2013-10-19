# -*- coding: utf-8 -*-

import hashlib

from django.db import models
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse_lazy


class Folder(models.Model):
    class Meta:
        ordering = ['-is_inbox', 'name']

    name = models.CharField(u'Имя', max_length = 64)

    is_inbox   = models.BooleanField()


    def __unicode__(self):
        return self.name or u'<папка>'

    def get_absolute_url(self):
        return reverse_lazy('folder', kwargs = { 'pk': self.id })

    @staticmethod
    def get_inbox():
        return Folder.objects.get(is_inbox = True)



class BaseArea(models.Model):
    class Meta:
        abstract = True

    address = models.CharField(u'Адрес', max_length = 256)

    x = models.FloatField(default = 43.95)
    y = models.FloatField(default = 56.30)
    zoom = models.IntegerField(default = 10)

    marks = models.CharField(max_length = 2048, blank = True)

    def __unicode__(self):
        return u'[{0}] {1}'.format(self.number, self.address)



def default_number():
    from django.db import connection
    c = connection.cursor()
    try:
        c.execute('''
            SELECT number
            FROM areas_area
            WHERE number = 1
            LIMIT 1
        ''')
        if not c.fetchone():
            return 1

        c.execute('''
            SELECT t1.number + 1 AS missing
            FROM areas_area AS t1
            LEFT JOIN areas_area AS t2
                ON t1.number+1 = t2.number
            WHERE t2.number IS NULL
            ORDER BY t1.number
            LIMIT 1
        ''')
        row = c.fetchone()
        return row[0] if row else 1
    finally:
        c.close()


class Area(BaseArea):
    class Meta:
        ordering = ('number',)

    folder = models.ForeignKey(Folder, verbose_name = u'Папка')

    number = models.IntegerField(u'Номер участка', unique = True, default = default_number, error_messages = {
        'unique': u'Участок с таким номером уже есть'
    })


    def get_absolute_url(self):
        return reverse_lazy('area-edit', kwargs = { 'number': self.number })


    def archive(self):
        fields = {
            f.name: f.value_from_object(self)
            for f in self._meta.fields
        }
        del fields['id']
        del fields['folder']

        ArchivedArea(**fields).save()
        self.delete()


class ArchivedArea(BaseArea):
    class Meta:
        ordering = ('number',)

    number = models.IntegerField(u'Номер участка')

    def get_absolute_url(self):
        return reverse_lazy('archive-edit', kwargs = { 'pk': self.id })

    def restore_to(self, folder):
        fields = {
            f.name: f.value_from_object(self)
            for f in self._meta.fields
        }
        del fields['id']

        fields['folder'] = folder

        Area(**fields).save()
        self.delete()



class MapCache(models.Model):
    urlhash = models.CharField(max_length = 40, unique = True)
    url = models.CharField(max_length = 2048)

    def _gen_filename(self, filename):
        return 'mapcache/{0}/{1}'.format(filename[:2], filename)

    map = models.FileField(upload_to = _gen_filename)


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
