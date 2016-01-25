from django.shortcuts import render_to_response
from django.template import RequestContext


def render_to(template):
    """
    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request))
            return output
        return wrapper
    return renderer




# From http://blog.brendel.com/2012/01/django-modelforms-setting-any-field.html
from django import forms
class ExtendedMetaModelForm(forms.ModelForm):
    """
    Allow the setting of any field attributes via the Meta class.
    """
    def __init__(self, *args, **kwargs):
        """
        Iterate over fields, set attributes from Meta.field_args.
        """
        super(ExtendedMetaModelForm, self).__init__(*args, **kwargs)
        if hasattr(self.Meta, "field_args"):
            # Look at the field_args Meta class attribute to get
            # any (additional) attributes we should set for a field.
            field_args = self.Meta.field_args
            # Iterate over all fields...
            for fname, field in self.fields.items():
                # Check if we have something for that field in field_args
                fargs = field_args.get(fname)
                if fargs:
                    # Iterate over all attributes for a field that we
                    # have specified in field_args
                    for attr_name, attr_val in fargs.items():
                        if attr_name.startswith("+"):
                            merge_attempt = True
                            attr_name = attr_name[1:]
                        else:
                            merge_attempt = False
                        orig_attr_val = getattr(field, attr_name, None)
                        if orig_attr_val and merge_attempt and \
                                    type(orig_attr_val) == dict and \
                                    type(attr_val) == dict:
                            # Merge dictionaries together
                            orig_attr_val.update(attr_val)
                        else:
                            # Replace existing attribute
                            setattr(field, attr_name, attr_val)



from django.views.generic.edit import UpdateView
from django.core.exceptions import PermissionDenied

class UpdateViewExtPerms(UpdateView):
    save_permission = None

    def post(self, request, *args, **kwargs):
        if self.save_permission is not None:
            if not request.user.has_perm(self.save_permission):
                raise PermissionDenied()

        return super(UpdateViewExtPerms, self).post(request, *args, **kwargs)
