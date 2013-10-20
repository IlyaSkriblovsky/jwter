from django.utils.decorators import method_decorator


def class_decorator(dec):
    def wrapper(cls):
        cls.dispatch = method_decorator(dec)(cls.dispatch)
        return cls

    return wrapper
