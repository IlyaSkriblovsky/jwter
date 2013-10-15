import urllib

from django import template

register = template.Library()


@register.tag
def paginator(parser, token):
    args = token.split_contents()
    template_tag = args[0]
    return PaginatorNode(args[1:])


class PaginatorNode(template.Node):
    def __init__(self, args):
        pass

    def render(self, context):
        getvars = context['request'].GET.copy()
        try: del getvars['page']
        except KeyError: pass

        if len(getvars) > 0:
            context['paginator_getvars'] = u'&' + getvars.urlencode()
        else:
            context['paginator_getvars'] = u''

        t = template.loader.get_template('paginator.html')
        return t.render(context)
