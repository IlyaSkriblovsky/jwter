class SmartListMixin(object):
    model = None

    def _get_filters(self):
        filters = {}
        for arg in (a for a in self.request.GET.keys() if a.startswith('f_')):
            fieldname = arg[2:]
            value = self.request.GET[arg]

            if fieldname in self.list_fields and value:
                filters[fieldname] = self.request.GET[arg]

        return filters


    def _get_order(self):
        if 'order' in self.request.GET:
            order = self.request.GET['order']

            # if order in self.list_fields or '-{0}'.format(order) in self.list_fields:
            if order in self.list_fields or (order and order[0] == '-' and order[1:] in self.list_fields):
                return order

        return None


    def get_queryset(self):
        qs = self.model.objects.select_related(
            *[f.split('__')[0] for f in self.list_fields]
        )

        order = self._get_order()
        if order:
            qs = qs.order_by(self.request.GET['order'])


        for field, value in self._get_filters().items():
            qs = qs.filter(**{
                field + '__icontains': value
            })


        return qs


    def get_context_data(self, **kwargs):
        filters = self._get_filters()

        getvars_wo_order = self.request.GET.copy()
        try: del getvars_wo_order['order']
        except KeyError: pass

        if len(getvars_wo_order) > 0:
            args_wo_order = '&' + getvars_wo_order.urlencode()
        else:
            args_wo_order = ''

        order = self._get_order()

        t_list_fields  = []
        for field_name in self.list_fields:
            cur_model = self.model
            for part in field_name.split('__'):
                field = cur_model._meta.get_field(part)
                cur_model = field.rel.to if field.rel else None


            field_order = None
            order_link = '?order={0}{1}'.format(field_name, args_wo_order)
            if order == field_name:
                field_order = 'asc'
                order_link = '?order=-{0}{1}'.format(field_name, args_wo_order)
            elif order == '-' + field_name:
                field_order = 'dsc'


            t_list_fields.append({
                'field'       : field,
                'name'        : field_name,
                'verbose_name': field.verbose_name,
                'filter'      : filters[field_name] if field_name in filters else u'',
                'order'       : field_order,
                'order_link'  : order_link,
            })


        kwargs['list_fields'] = t_list_fields

        return super(SmartListMixin, self).get_context_data(**kwargs)
