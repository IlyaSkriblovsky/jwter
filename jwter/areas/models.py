# -*- coding: utf-8 -*-

import hashlib

from django.db import models
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse_lazy


class Folder(models.Model):
    class Meta:
        verbose_name=u'Папка'
        verbose_name=u'Папки'
        ordering = ['-is_inbox', 'name']
        permissions = (
            ('can_move_all', 'Can move all areas to another folder'),
        )

    name = models.CharField(u'Имя', max_length = 64)

    is_inbox   = models.BooleanField(editable=False)

    prefix = models.CharField(u'Префикс', max_length = 32, unique = True)


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



# def default_number():
#     from django.db import connection
#     c = connection.cursor()
#     try:
#         c.execute('''
#             SELECT number
#             FROM areas_area
#             WHERE number = 1
#             LIMIT 1
#         ''')
#         if not c.fetchone():
#             return 1

#         c.execute('''
#             SELECT t1.number + 1 AS missing
#             FROM areas_area AS t1
#             LEFT JOIN areas_area AS t2
#                 ON t1.number+1 = t2.number
#             WHERE t2.number IS NULL
#             ORDER BY t1.number
#             LIMIT 1
#         ''')
#         row = c.fetchone()
#         return row[0] if row else 1
#     finally:
#         c.close()


class Area(BaseArea):
    class Meta:
        verbose_name=u'Участок'
        verbose_name_plural=u'Участки'
        ordering = ('number',)
        permissions = (
            ('can_archive', 'Can delete areas to Trash'),
        )
        unique_together = (('folder', 'number'),)

    folder = models.ForeignKey(Folder, verbose_name = u'Папка')

    number = models.IntegerField(u'Номер участка')  # , default = default_number)


    @classmethod
    def first_free_number(cls, folder):
        from django.db import connection
        c = connection.cursor()
        try:
            c.execute('''
                SELECT number
                FROM areas_area
                WHERE folder_id=%s AND number=1
                LIMIT 1
            ''', [folder.id])
            if not c.fetchone():
                return 1

            c.execute('''
                SELECT t1.number + 1 AS missing
                FROM areas_area AS t1
                LEFT JOIN areas_area AS t2
                    ON t1.number+1=t2.number AND t1.folder_id=t2.folder_id
                WHERE t1.folder_id=%s AND t2.number IS NULL
                ORDER BY t1.number
                LIMIT 1
            ''', [folder.id])
            row = c.fetchone()
            return row[0] if row else 1
        finally:
            c.close()


    def get_absolute_url(self):
        return reverse_lazy('area-edit', kwargs = { 'folder_id': self.folder.id, 'number': self.number })

    def formatted_number(self):
        return u'{}–{}'.format(self.folder.prefix, self.number)

    def archive(self):
        ArchivedArea.create_from(self).save()
        self.delete()


class ArchivedArea(BaseArea):
    class Meta:
        ordering = ('number',)
        permissions = (
            ('can_view_archive', 'Can view archive'),
            ('can_restore', 'Can restore area'),
        )

    folder_prefix = models.CharField(u'Префикс', max_length = 32)

    number = models.IntegerField(u'Номер участка')

    def get_absolute_url(self):
        return reverse_lazy('archive-edit', kwargs = { 'pk': self.id })

    def formatted_number(self):
        return u'{}-{}'.format(self.folder_prefix, self.number)

    @classmethod
    def create_from(self, area):
        fields = {
            f.name: f.value_from_object(area)
            for f in area._meta.fields
        }
        del fields['id']
        del fields['folder']
        fields['folder_prefix'] = area.folder.prefix

        return ArchivedArea(**fields)

    def restore_to(self, folder):
        fields = {
            f.name: f.value_from_object(self)
            for f in self._meta.fields
        }
        del fields['id']
        del fields['folder_prefix']

        fields['folder'] = folder

        print(fields)

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
